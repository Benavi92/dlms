from django.urls import path
from .views import test_


urlpatterns = [
    path("list", test_)
]