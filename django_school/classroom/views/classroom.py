from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from ..models import Student

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:quiz_change_list')
        elif request.user.is_student:
            return redirect('students:quiz_list')
        else:
            return redirect('admin:index')
    return redirect('login') # render(request, 'classroom/home.html')


def save_github_user(backend, user, response, *args, **kwargs):
    if backend.name == 'github':
        if not user.is_student:
            user.is_student = True
            user.save()
            student = Student.objects.create(user=user)
        # avatar_url = response.get('avatar_url')
        # print(user, response)

