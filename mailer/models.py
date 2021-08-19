from __future__ import unicode_literals

from datetime import datetime

import datetime

from django.utils.timezone import now as datetime_now
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.conf import settings

from django.core.mail import EmailMessage

from django.utils.timezone import now



RESULT_SUCCESS = "1"
RESULT_DONT_SEND = "2"
RESULT_FAILURE = "3"
RESULT_QUERY = "4"

RESULT_CODES = (
    (RESULT_SUCCESS, "Відправленно"),
    (RESULT_DONT_SEND, "Не відправленно"),
    (RESULT_FAILURE, "Помилка"),
    (RESULT_QUERY, "У черзі")
    # @@@ other types of failure?
)


# emails models
class Email_addres(models.Model):
    """
    единица почтового адреса
    addres - адрес почты
    name - человеко читаймое название
    crypt - указывает являеться ли этот адрес защищенным
    """
    addres = models.EmailField(unique=True)
    name = models.CharField(max_length=250, blank=True)
    crypt = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.addres


class Mail(models.Model):
    """
    Модель почтового отправления - используеться для хранения информаций об отправленном сообщений,
     логах, файлах

    """
    id = models.AutoField(primary_key=True)
    # почтовые параметры
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sender',
                               verbose_name="отправитель")  # кто?
    to = models.ManyToManyField(Email_addres, verbose_name="получатели")  # куда?
    date_create = models.DateTimeField(auto_now_add=True)  # когда добавили
    date_send = models.DateTimeField(blank=True, null=True)  # когда отправленно
    title = models.TextField(verbose_name="Тема письма")  # тема
    body = models.TextField(verbose_name="Тело письма", blank=True, null=True)  # тело

    mailbox_key = models.CharField(blank=True, max_length=250)

    logs = models.ManyToManyField('MessageLog', blank=True)  # Логи

    status = models.CharField(max_length=4,
                              choices=RESULT_CODES,
                              default=RESULT_QUERY)

    files = models.OneToOneField('FilePool',
                                 on_delete=models.DO_NOTHING,
                                 related_name='mail_files', blank=True, null=True)

    def __str__(self):
        return f"№ {self.id}, тема:{self.title}"

    def get_status(self):
        """
        получаем человеко читаймый статус вместо кода
        :return:
        """
        for status in RESULT_CODES:
            if self.status == status[0]:
                return status[1]

    def create_email(self):
        """
        создаем почтовое отправление на основе данных в моделе
        :return:
        """
        email = EmailMessage()
        email.sender = self.sender
        email.subject = self.title
        email.body = self.body

        if self.files != None:
            for file in self.files.files.all():
                file_path = file.url.replace("/storege/", settings.MEDIA_ROOT)
                email.attach_file(file_path)

        to = []  # куда
        for email_addres in self.to.all():
            to.append(Email_addres.objects.get(addres=email_addres).addres)
        email.to = to

        return email


def get_path_file_upload(instance, filename):
    name = str(instance.mail.sender.name)
    today = datetime.now()
    return f'user_{name}/{today.year}/{today.month}/{today.day}/{filename}'


class GrupMail(models.Model):
    name = models.CharField(max_length=60)
    sender = models.OneToOneField(User, on_delete=models.DO_NOTHING, unique=True)
    list_mails = models.ManyToManyField('Email_addres')

    def __str__(self):
        return '%s' % self.name


class FilePool(models.Model):
    """
    Пул(набор) файлов завязанных на объекте Mail
    """
    files = models.ManyToManyField('FileSend')


class FileSend(models.Model):
    """
    Файл для отпраки привязаный к пулу
    """
    name = models.CharField(max_length=150, blank=True)
    file_path = models.FilePathField(path=settings.MEDIA_ROOT, max_length=255)

    url = models.CharField(max_length=350, blank=True)

    def __str__(self):
        return 'file:%s' % (self.name)


class MessageLogManager(models.Manager):

    def log(self, mail, result_code, log_message=""):
        """
        create a log entry for an attempt to send the given message and
        record the given result and (optionally) a log message
        """
        return self.create(
            message_id=mail.id,
            when_added=datetime_now(),
            # @@@ other fields from Message
            result=result_code,
            log_message=log_message,
        )

    def purge_old_entries(self, days):
        limit = datetime_now() - datetime.timedelta(days=days)
        query = self.filter(when_attempted__lt=limit, result=RESULT_SUCCESS)
        count = query.count()
        query.delete()
        return count


class MessageLog(models.Model):

    message_id = models.TextField(editable=False, null=True, verbose_name="Номер отправление")
    when_added = models.DateTimeField(db_index=True, verbose_name="дата создания")

    # additional logging fields
    when_attempted = models.DateTimeField(default=datetime_now)
    result = models.CharField(max_length=1, choices=RESULT_CODES, verbose_name="Результат")
    log_message = models.TextField()

    objects = MessageLogManager()

    class Meta:
        verbose_name = _("message log")
        verbose_name_plural = _("message logs")


    def __str__(self):
        return f"log_{self.id} Отправление №_{self.message_id}"

    # def __str__(self):
    #     try:
    #         email = self.email
    #         return "Mail {0}, \"{1}\" to {2}".forma
    #
    #     except Exception:
    #         return "<MessageLog repr unavailable>"

    def get_status(self):
        for status in RESULT_CODES:
            if self.result == status[0]:
                return status[1]


choices_ZapEmailAdd = [('1', 'Не обробленно'),
                       ('2', 'готово')]


class ZapEmailAdd(models.Model):
    """
    запрос на добавления нового адреса для конкретного пользователя
    когда, кто, что? зачем?
    """
    id = models.AutoField(primary_key=True)
    date_wenadd = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)

    # 1 - не обработанно, 2 - готово
    status = models.CharField(max_length=1,
                              choices=choices_ZapEmailAdd,
                              default='1')

    name = models.CharField(max_length=250, blank=True)

    email_addres = models.EmailField()
    text = models.TextField()

    def __str__(self):
        return '%s' % self.email_addres


# Входящяя почта
class IncomeMail(models.Model):
    """
    представление входящего сообщения, загружаем полностью если получили из доверенного источника
    (есть в списке адресов)
    """
    # sender = models.CharField(max_length=250, verbose_name="Відправник")
    from_Box = models.ForeignKey("ExternalMailBox", on_delete=models.DO_NOTHING, verbose_name="завантаженно з",
                                 null=True, blank=True)
    sender = models.ForeignKey(Email_addres, on_delete=models.CASCADE, )
    data_income = models.DateTimeField(blank=True, auto_now=True, verbose_name="Дата отримання")
    data_send = models.DateTimeField(blank=True, verbose_name="Дата відправки")

    to = models.CharField(max_length=250, verbose_name="Отримувачі")

    uid_box = models.CharField(max_length=500, default="None", verbose_name="UID поштової скриньки")
    title = models.TextField(blank=True, null=True, verbose_name="Тема")  # тема
    body = models.TextField(blank=True, null=True, verbose_name="Тіло листа")  # тело

    mailbox_key = models.CharField(blank=True, max_length=250)

    is_full_loaded = models.BooleanField(verbose_name="Завантеженно", default=False)

    files = models.OneToOneField('FilePool',
                                 on_delete=models.DO_NOTHING,
                                 related_name='incomeMail', blank=True, null=True)
    class Meta:
        verbose_name = ("Вхідна кореспонденція")
        verbose_name_plural = ("Вхідна кореспонденція")

        unique_together = ('uid_box', 'from_Box',)

    def __str__(self):
        return f"{self.id} {self.sender} {self.title}"


class ExternalMailBox(models.Model):
    """
    представление внешнего почтового ящика
    """
    is_active = models.BooleanField(default=False, verbose_name="статус")
    host = models.CharField(max_length=200, verbose_name="сервер")
    port = models.IntegerField(verbose_name="порт")
    user = models.CharField(max_length=200, verbose_name="учетная запись")
    psw = models.CharField(max_length=32)

    protocol = models.CharField(max_length=30, choices=[("POP", "POP"),
                                                        ("IMAP", "IMAP")])

    crypt = models.CharField(max_length=30, choices=[("None", "None"),
                                                     ("STARTTLS", "STARTTLS"),
                                                     ("SSL/TLS", "SSL/TLS")])

    auth_method = models.CharField(max_length=30, choices=[("None", "None"),
                                                           ("pasw", "pasw"),
                                                           ("Kerberos/GSSAPI", "Kerberos/GSSAPI")])

    def __str__(self):
        return f"{self.user}"
