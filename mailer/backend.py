from __future__ import unicode_literals

from django.core.mail.backends.base import BaseEmailBackend

from .models import Mail, Email_addres


class DbBackend(BaseEmailBackend):

    def send_messages(self, email_messages):

        for num, email in enumerate(email_messages):
            mail = Mail.objects.create()

            mail.sender = email.sender
            mail.title = email.subject
            mail.body = email.body
            mail.files = email.filepoll

            for email_addres in email.to:
                mail.to.add(Email_addres.objects.get(addres=email_addres))

            mail.save()


        return len(email_messages)
