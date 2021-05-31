# Rest Framework
from rest_framework import serializers

# Models
from classroom.models import Quiz


class QuizModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ('owner', 'name', 'subject')
