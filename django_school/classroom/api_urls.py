# Django
from django.urls import include, path
from django.conf import settings

# Importing Django rest libraries.
from rest_framework.routers import DefaultRouter, SimpleRouter

# Views
from classroom.api.quiz import QuizViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("", QuizViewSet, basename='workers')

urlpatterns = [
    path('', include(router.urls))
]
