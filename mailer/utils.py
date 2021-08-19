import mailbox
import email
import os
import poplib
from datetime import datetime
from django.conf import settings
from .models import IncomeMail, FilePool, FileSend, Email_addres, ExternalMailBox
import re
import base64
import sys


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


# mbox = mailbox.Maildir("income", create=False)
search = re.compile(r"([\w\.\-_]*@[\w\.\-_]*)")

msg = email.message.Message

def mailbox_save(msg, box):
    mbox = mailbox.Maildir(box, create=False)
    key = mbox.add(msg)
    mbox.flush()
    return key


def get_save_directory(id):
    # MEDIA_ROOT\INCOME\MONTH_YEAR_DAY\id_time

    date = datetime.now()
    path = f'{ settings.MEDIA_ROOT }income/{date.day}_{date.month}_{date.year}/{ id }_{date.hour}.{date.minute}'
    url = f'/storege/income/{date.day}_{date.month}_{date.year}/{ id }_{date.hour}.{date.minute}'
    i = 1
    while True:
        if os.path.exists(path + '_%d/' % i):
            i += 1
        else:
            path += '_%d/' % i
            url += '_%d/' % i
            break

    return path, url


def get_mail(mail, uid, key, external_box=None):
    """
    собираем информацию из отправления
    :param mail:
    :return:
    """

    # From = mail['From']
    # To = mail['To']
    # data_sand = datetime.strptime(mail["Date"], "%a, %d %b %Y %H:%M:%S %z")
    # title = email.header.decode_header(mail['Subject'])[0][0]
    print(uid)
    result_decoe_header = email.header.decode_header(mail["From"])

    addres = Email_addres.objects.get(addres=search.findall(str(mail["From"]))[0])
    # выборка темы
    if mail['Subject']:
        title, codepage = email.header.decode_header(mail['Subject'])[0]
        title = title if isinstance(title, str) else title.decode(codepage if codepage is not None else "utf8")
    else:
        title = ""
    # время отправки
    try:
        data_send = datetime.strptime(mail["Date"], "%a, %d %b %Y %H:%M:%S %z")
    except ValueError:
        print("data is not valid", mail["Date"])
        data_send = datetime.now()

    to = search.findall(str(mail['To']))
    to_instance = " ".join(to)

    if IncomeMail.objects.filter(uid_box=uid).exists():
        print("сообщение с таким UID уже существует")
        return

    income = IncomeMail.objects.create(uid_box=uid,
                                       sender=addres,
                                       data_send=data_send,
                                       to=to_instance[:250],
                                       title=title,
                                       mailbox_key=key,
                                       from_Box=external_box)

    # income.sender = addres
    # income.to = mail['To']
    # income.data_send = datetime.strptime(mail["Date"], "%a, %d %b %Y %H:%M:%S %z")
    # income.title = email.header.decode_header(mail['Subject'])[0][0]

    full_body = ""

    # t = mail.get_payload()
    files = []

    for elem in mail.walk():
        if elem.get_filename() is None:
            print(elem.get_content_maintype())
            if elem.get_content_maintype() == "text":
                try:
                    body = ""
                    if elem.get("Content-Transfer-Encoding") == "7bit":
                        print(elem.get("Content-Transfer-Encoding"))
                        body, codepage = email.header.decode_header(elem.get_payload())[0]

                        body = body if isinstance(body, str) else body.decode(
                            codepage if codepage is not None else "utf8")


                    elif elem.get("Content-Transfer-Encoding") == "base64":
                        print(elem.get("Content-Transfer-Encoding"))

                        body = base64.b64decode(elem.get_payload()).decode()

                    elif elem.get("Content-Transfer-Encoding") == "8bit":

                        print(elem.get("Content-Transfer-Encoding"))
                        text = elem.get_payload()
                        if isinstance(text, str):
                            body = text
                            # b = bytes(elem.get_payload(), encoding="cp1251")
                            # body = b.decode("utf8" ,"ignore")

                        else:
                            body = elem.get_payload().encode("cp1251").decode("utf8", "ignore")
                    if body:
                        full_body += body

                except (TypeError, ValueError, UnicodeDecodeError):
                    print("can't decode body")
                    # body =

                # body = elem.get_payload()
                # body, codepage = email.header.decode_header(body)[0]
                # body = body if isinstance(body, str) else body.decode(codepage if codepage is not None else "utf8")
                # print(body)
        else:
            filename, codepage = email.header.decode_header(elem.get_filename())[0]
            filename = filename if isinstance(filename, str) else filename.decode(codepage if codepage is not None else "utf8")

            path, url = get_save_directory(income.id)
            print(filename, path)
            os.makedirs(path, exist_ok=True)
            path = os.path.join(path, filename)
            file = open(path, 'wb')
            try:
                file.write(elem.get_payload(decode=True))
                file.close()
            except TypeError:
                payload_file = elem.get_payload()
                if isinstance(payload_file, bytes):
                    file.write(payload_file)

                elif isinstance(payload_file, str):
                    try:
                        file.write(payload_file.encode("utf8"))
                    except:
                        pass 
                file.close()

            filesend = FileSend.objects.create(name=filename,
                                               file_path=path,
                                               url=url + filename)
            filesend.save()
            files.append(filesend)



    if files:
        filepool = FilePool.objects.create()
        for file in files:
            filepool.files.add(file)
        filepool.save()
        income.files = filepool

    income.body = full_body
    income.save()



def connect_mailbox():
    # get_corrent_incomeMail(b"MD50000009564:MSG:28684:30818242:2238804192")
    # return
    safe_addres = [x.addres for x in list(Email_addres.objects.all())]

    boxs = ExternalMailBox.objects.all()
    for externalbox in boxs:
        if not externalbox.is_active:
            continue

        try:
            box = poplib.POP3(externalbox.host, externalbox.port)
            box.user(externalbox.user)
            box.pass_(externalbox.psw)
        except poplib.error_proto:
            print("error connect to box")
            print(sys.exc_info())
            continue
        response, lts, other = box.uidl()

        # lts = [b'1 MD50000009547:MSG:38387:30817877:3333953200']
        print(lts)

        for elem in lts:
            num_msg, uid = elem.decode("utf8").split()
            print(uid)
            if IncomeMail.objects.filter(uid_box=uid, from_Box=externalbox).exists():
                print("сообщение с таким UID уже существует")
                continue

            (resp, lines, octets) = box.retr(num_msg)

            msgtext = "\n".join(map(lambda x: x.decode("utf8", "ignore"), lines)) +"\n\n"
            massage = email.message_from_string(msgtext)

            mail_addres = search.findall(str(massage["From"]))
            if not mail_addres:
                print("can't parse sender")
                print(str(massage["From"]))
                continue

            if mail_addres[0] in safe_addres:
                print("it's safe")
                key = mailbox_save(b"\n".join(lines) + b"\n\n", "income")
                get_mail(massage, uid, key, externalbox)
            else:
                print("не провереный отправитель")

        box.rset()
        box.quit()


def get_corrent_incomeMail(serched_uid):
    "MD50000009564:MSG:28684:30818242:2238804192"
    box = poplib.POP3(settings.EMAIL_HOST, 110)
    box.user(settings.EMAIL_HOST_USER)
    box.pass_(settings.EMAIL_HOST_PASSWORD)

    response, lts, other = box.uidl()

    for answ in lts:
        if serched_uid in answ:

            num_msg, uid = answ.decode("utf8").split()

            (resp, lines, octets) = box.retr(num_msg)

            msgtext = "\n".join(map(lambda x: x.decode("utf8"), lines)) + "\n\n"
            massage = email.message_from_string(msgtext)

            mail_addres = search.findall(str(massage["From"]))
            if not mail_addres:
                continue

            key = mailbox_save(b"\n".join(lines) + b"\n\n", "income")
            get_mail(massage, uid, key)

    box.rset()
    box.quit()


def test_utf():

    import base64
    row = '''=?UTF-8?B?RndkOiDQndC+0LLQvtC1INGB0L7QvtCx0YnQtdC90LjQtSDQvtGCINCc0LXQttC00YPQvQ==?=
    	=?UTF-8?B?0LDRgNC+0LTQvdCw0Y8g0JDQutCw0LTQtdC80LjRjyDQn9GA0L7RhNC10YHRgdC40L7QvdCw0LvRjNC9?=
    	=?UTF-8?B?0L7Qs9C+INCa0L7Rg9GH0LjQvdCz0LAgSUFQQyAtINCg0LXQs9C40YHRgtGA0LDRhtC40Y8g0JrQotCe?='''

    text, encoding = email.header.decode_header(row)[0]


    print(text.decode('utf8'))
    print(encoding)
# test_utf()
