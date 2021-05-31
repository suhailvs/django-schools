# Django
from django.urls import include, path
from django.conf import settings

# Django Rest Framework
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

app_name = "api"

urlpatterns = [
    path('quiz/', include('classroom.api_urls')),
]
