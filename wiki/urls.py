from django.urls import path
from .views import correntupdate, main, correntprogram

# mails/sendtest/
urlpatterns = [
    path('', main),
    path('program/<str:program>', correntprogram),
    path('program/<str:program>/<int:id>', correntupdate)
]