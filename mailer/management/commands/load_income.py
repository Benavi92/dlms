import logging
from django.core.management.base import BaseCommand
from mailer.utils import connect_mailbox
import time


class Command(BaseCommand):
    help = "load income mails"

    def handle(self, *args, **options):

        # Compatiblity with Django-1.6
        logging.info("start load mails")
        connect_mailbox()

        while True:
            time.sleep(600)
            logging.info("load session")
            connect_mailbox()



"""
для получения адекватной информаций из письма:
изначально в хедере лежит мета информация - кто куда когда что

тема - нужно на email['Subject'] использовать email.header.decode_header
text = email.header.decode_header(i['Subject'])[0][0]

email.get_payload(i=None, decode=False) - получить "полезную нагрузку"

        # Here is the logic table for this code, based on the email5.0.0 code:
        #   i     decode  is_multipart  result
        # ------  ------  ------------  ------------------------------
        #  None   True    True          None                           - не нужно
        #   i     True    True          None                           - не нужно
        #  None   False   True          _payload (a list)
        #   i     False   True          _payload element i (a Message)
        #   i     False   False         error (not a list)             - не нужно
        #   i     True    False         error (not a list)             - не нужно
        #  None   False   False         _payload
        #  None   True    False         _payload decoded (bytes)


результат - зависит от is_multipart - если
    True - список объектов Massage,
    False - строку - когда в теле нету ничего - ни фалов ни сообщения
:
получение объекта Massage - в котором храниться часть сообщения - для получения типа данных там хранящихся
используеться get_content_type():
    "text/plain" - текст - как правило тело письма
остально как правило вложение -
    для разпаковки необходимо использовать get_payload(decode=True) - получаем байтовый объект
    можно получить имя файла .get_filename()

"""
