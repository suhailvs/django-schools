# Django

# Rest framework
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

# Models
from classroom.models import Quiz

# Serializers
from classroom.serializers.quiz_serializer import QuizModelSerializer


class QuizViewSet(ListModelMixin, GenericViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizModelSerializer
