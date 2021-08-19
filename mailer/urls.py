from django.urls import path
from .views import (email_lists, corrent_mail, email_send_form, sendtest,
                    email_add, resend_email, test_html, list_zap, email_add_accept, add_emails_to_grupe,
                    re_create_mail, list_incomeMail, get_corrent_incomMail, )

# mails/sendtest/
urlpatterns = [
    path('emailadd/', email_add, name='emailadd'),
    path('', email_lists),
    path('allmails/', email_lists, name='email_lists'), # список отправлений
    path('<int:id>/', corrent_mail), # конкретное отправление
    path('mailsend/', email_send_form, name='email_send_form'), # форма для отправки

    path('re_create_mail/<int:id>/', re_create_mail),  # переотправка
    path('resends/<int:id>/', resend_email), # 
    path('sendtest/', sendtest), # отправка 
    path('testhtml/', test_html),
    path('list_zap/', list_zap),
    path('list_zap/email_add_accept/<int:id>/', email_add_accept),
    path('addtogrupe/',add_emails_to_grupe),
    path('income/', list_incomeMail),
    path('income/<int:id>', get_corrent_incomMail),


]
