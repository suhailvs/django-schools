import os
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.views import View
from ..decorators import teacher_required
from ..forms import (BaseAnswerInlineFormSet, QuestionForm, TeacherSignUpForm,
    QuizForm,QuestionsFileForm)
from ..models import Answer, Question, Quiz, Subject

User = get_user_model()

class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('teachers:quiz_change_list')


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'classroom/teachers/quiz_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .select_related('subject') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True))
        return queryset

@method_decorator([login_required, teacher_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'subject', )
    template_name = 'classroom/teachers/quiz_add_form.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('teachers:quiz_change', quiz.pk)


def create_question(quiz,line):
    DELIMITER = '|'
    items = line.strip().split(DELIMITER)
    correct_index=items[-1]
    explanation=''
    if ':explanation:' in correct_index:
        correct_index,explanation=correct_index.split(':explanation:')
    question = Question.objects.create(quiz = quiz, text = items[0],explanation=explanation)    
    correct_index = int(correct_index)
    for i,ans in enumerate(items[1:-1]):
        Answer.objects.create(question = question, text = ans.strip(), is_correct=(correct_index==i+1))


@login_required
@teacher_required
def quiz_update(request, pk):
    quiz = get_object_or_404(Quiz,pk=pk,owner=request.user)

    # ---------- QUIZ UPDATE FORM ----------
    if request.method == 'POST' and request.POST.get('action') == 'update_quiz':
        quiz_form = QuizForm(request.POST, instance=quiz)
        upload_form = QuestionsFileForm()

        if quiz_form.is_valid():
            quiz_form.save()
            return redirect('teachers:quiz_change', pk=quiz.pk)

    # ---------- FILE UPLOAD FORM ----------
    elif request.method == 'POST' and request.POST.get('action') == 'upload_questions':
        quiz_form = QuizForm(instance=quiz)
        upload_form = QuestionsFileForm(request.POST, request.FILES)

        if upload_form.is_valid():
            uploaded_file = upload_form.cleaned_data['file']
            lines = uploaded_file.read().decode('utf-8').splitlines()
            with transaction.atomic():
                for line in lines:
                    if line.strip():create_question(quiz, line)
            return redirect('teachers:quiz_change', pk=quiz.pk)

    # ---------- GET REQUEST ----------
    else:
        quiz_form = QuizForm(instance=quiz)
        upload_form = QuestionsFileForm()

    return render(request, 'classroom/teachers/quiz_change_form.html', {
        'quiz': quiz,
        'form': quiz_form,
        'frm_fileupload': upload_form,
        'questions': quiz.questions.annotate(answers_count=Count('answers')),
    })

@method_decorator([login_required, teacher_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'classroom/teachers/quiz_delete_confirm.html'
    success_url = reverse_lazy('teachers:quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizResultsView(DetailView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'classroom/teachers/quiz_results.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related('student__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score,
            'total_questions':quiz.questions.count()
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@login_required
@teacher_required
def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('teachers:question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'classroom/teachers/question_add_form.html', {'quiz': quiz, 'form': form})


@login_required
@teacher_required
def question_change(request, quiz_pk, question_pk):
    # Simlar to the `question_add` view, this view is also managing
    # the permissions at object-level. By querying both `quiz` and
    # `question` we are making sure only the owner of the quiz can
    # change its details and also only questions that belongs to this
    # specific quiz can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

    AnswerFormSet = inlineformset_factory(
        Question,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('text', 'is_correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('teachers:quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'classroom/teachers/question_change_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset
    })


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'classroom/teachers/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('teachers:quiz_change', kwargs={'pk': question.quiz_id})

@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionPreviewView(DetailView):
    model = Question 
    template_name = 'classroom/teachers/question_preview.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)

@method_decorator([login_required, teacher_required], name='dispatch')
class QuizBulkAddView(View):
    def add_quiz(self,subject, quiz_name):
        obj_subj, _ = Subject.objects.get_or_create(name = subject.replace('_',' '))
        filename = os.path.join(self.folderpath, subject, '{0}.txt'.format(quiz_name))
        if Quiz.objects.filter(name=quiz_name, subject=obj_subj):
            return f'Skipped file: {filename}'
        quiz= Quiz.objects.create(owner = self.request.user, name=quiz_name, subject=obj_subj)
        fp = open(filename,'r')
        print(f'Processing file: {filename}')
        for line in fp.readlines():
            create_question(quiz,line)
        return f'Added file: {filename}'

    def get(self, request):
        result = ''
        self.folderpath = 'classroom/fixtures/quizzes'
        with transaction.atomic():
            for r, d, f in os.walk(self.folderpath):
                for file in f:
                    if ".txt" in file:
                        subject = r.rsplit('/',1)[1]
                        quiz_name = file.split('.')[0]                    
                        result+= self.add_quiz(subject,quiz_name)+', '
        messages.success(self.request, f'Following files processed: {result}')
        return redirect('teachers:quiz_change_list')
       