from rest_framework import viewsets
from classroom.models import Quiz
from classroom.serializers import QuizSerializer


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
