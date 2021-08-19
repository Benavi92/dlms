from django.urls import path
from .views import MailView, DfsView


app_name = "articles"


# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('mails/', MailView.as_view()),
    path('mails/<int:id>', MailView.as_view()),

    path('dfs/', DfsView.as_view()),
    path('dfs/<int:id>', DfsView.as_view()),
]

