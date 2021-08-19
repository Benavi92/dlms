from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Email_addres, GrupMail, Mail, FileSend, FilePool, MessageLog, ZapEmailAdd, IncomeMail
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from .engine import send_all
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from datetime import datetime
import smtplib
from socket import error as socket_error
from django.utils.timezone import now as datetime_now
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import mailbox
from django.contrib.auth.models import User
from .utils import connect_mailbox


RESULT_SUCCESS = "1"
RESULT_DONT_SEND = "2"
RESULT_FAILURE = "3"
RESULT_QUERY = "4"


def mailbox_save(email, box):
    mbox = mailbox.Maildir(box)
    key = mbox.add(email.message())
    mbox.flush()
    return key


class NewEmailMessage(EmailMessage):
    sender = None
    filepoll = None


def get_user_upload_directory(user, title):
    # MEDIA_ROOT\USER\MONTH_YEAR\DAY\TITLE & time

    date = datetime.now()
    path = f'{ settings.MEDIA_ROOT}{user.get_username()}/{date.month}_{date.year}/{date.day}/{ title }_{date.hour}.{date.minute}'
    url = f'/storage/{ user.get_username() }/{date.month}_{date.year}/{date.day}/{ title }_{date.hour}.{date.minute}'
    i = 1
    while True:
        if os.path.exists(path + '_%d/' % i):
            i += 1
        else:
            path += '_%d/' % i
            url += '_%d/' % i
            break

    return path, url


def main_view(request):
    return render(request, 'main.html')


@login_required
def email_lists(request, msg=None):

    def filter_query(query, word):
        return query.filter_query(Q(to__addres__icontains=word) |
                                  Q(to__name__icontains=word) |
                                  Q(sender__username__icontains=word) |
                                  Q(title__icontains=word) |
                                  Q(body__icontains=word)).distinct()

    search_query = request.GET.get('search', '')
    page_query = request.GET.get('page', '')
    # если есть поисковый запрос
    if search_query:
        if request.user.get_username() not in ['admin']:
            mails = Mail.objects.filter_query(sender__username__icontains=request.user.get_username()).order_by('-date_create')
        else:
            mails = Mail.objects.all().order_by('-date_create')
        for word in search_query.split():

            mails = filter_query(mails, word)
        paginator = Paginator(mails, 15)
        page = request.GET.get('page')

    # в отсальных случаях
    else:
        if request.user.get_username() not in ['admin', 'Уколова']:
            mails = Mail.objects.filter_query(sender__username__icontains=request.user.get_username()).order_by('-date_create')
        else:
            mails = Mail.objects.all().order_by('-date_create')
        paginator = Paginator(mails, 15)
        page = request.GET.get('page')

    try:
        mails = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mails = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mails = paginator.page(paginator.num_pages)
    pages = []
    if paginator.num_pages <= 5:
        pages = [x for x in paginator.page_range]
    elif mails.number:
        for x in paginator.page_range:
            if mails.number - 5 < x < mails.number + 5:
                pages.append(x)
    return render(request, 'email_list.html', context={'mails': mails,
                                                       'msg': msg,
                                                       'pages': pages,
                                                       "search_query": search_query})


@login_required
def corrent_mail(request, id):
    mail = get_object_or_404(Mail, id=id)
    return render(request, 'corrent_mail.html', context={'mail': mail})


@login_required
def email_send_form(request):
    """
    форма для отправления почты
    если метод POST - происходит попытка отправить почту
    adress - пул адресов достпных пользователю
    :param request:
    :return:
    """

    if request.user.get_username() not in ['admin']:
        try:
            adress = GrupMail.objects.get(sender=request.user).list_mails.all()
        except:
            adress = []
    else:
        adress = Email_addres.objects.all()

    if request.method == 'POST':
        mail = Mail.objects.create()
        request_info = request.POST
        mail.title = request_info['title']
        mail.sender = request.user
        mail.body = request_info['body']
        fs = FileSystemStorage()

        for email_id_addres in request_info.getlist('addres'):
            mail.to.add(Email_addres.objects.get(id=email_id_addres).id)

        if request.FILES.getlist('files'):
            filepool = FilePool.objects.create()

            for file in request.FILES.getlist('files'):

                path, url = get_user_upload_directory(mail.sender, mail.id)

                fs = FileSystemStorage(location=path)
                print(get_user_upload_directory(mail.sender, mail.id))
                # /01/ > D:\01
                #
                filename = fs.save(file.name, file)
                filesend = FileSend.objects.create(name=file.name,
                                                   file_path=os.path.join(path, file.name),
                                                   url=url + filename)
                filesend.save()
                filepool.files.add(filesend)

            filepool.save()
            mail.files = filepool
        mail.save()
        try:
            email = mail.create_email()
            email.send()
            mail.status = "1"
            mail.logs.add(MessageLog.objects.log(mail, RESULT_SUCCESS))
            mail.date_send = datetime_now()
            mail.mailbox_key = mailbox_save(email, 'sendet1')
            mail.save()

        except (socket_error, smtplib.SMTPSenderRefused,
                smtplib.SMTPRecipientsRefused,
                smtplib.SMTPDataError,
                smtplib.SMTPAuthenticationError) as err:
            mail.logs.add(MessageLog.objects.log(mail, RESULT_FAILURE, log_message=str(err)))
            mail.status = "4"
            mail.save()

            print(err)

        return corrent_mail(request, id=mail.id)

    return render(request, 'email_send_form.html', context={'adress': adress})


@login_required
def email_send_form_v2(request):
    """
    форма для отправления почты
    если метод POST - происходит попытка отправить почту
    adress - пул адресов достпных пользователю
    :param request:
    :return:
    """
    print(request.user.has_perm("mailer.add_mail"))
    if request.user.has_perm("mailer.add_mail"):
        adress = Email_addres.objects.all()
    elif not request.user.is_anonymous:
        adress = GrupMail.objects.get(sender=request.user).list_mails.all()

    if request.method == 'POST':
        mail = Mail.objects.create()
        request_info = request.POST
        mail.title = request_info['title']
        mail.sender = request.user
        mail.body = request_info['body']

        email = EmailMessage()
        email.subject = mail.title
        email.body = mail.body
        to = []

        for email_id_addres in request_info.getlist('addres'):
            to_adres = Email_addres.objects.get(id=email_id_addres)
            mail.to.add(to_adres.id)
            to.append(to_adres.addres)

        email.to = to

        if request.FILES.getlist('files'):
            fs = FileSystemStorage()
            filepool = FilePool.objects.create()
            for file in request.FILES.getlist('files'):
                path, url = get_user_upload_directory(mail.sender, mail.id)
                fs = FileSystemStorage(location=path)
                filename = fs.save(file.name, file)
                filesend = FileSend.objects.create(name=file.name,
                                                   file_path=os.path.join(path, file.name),
                                                   url=url + filename)
                filesend.save()
                filepool.files.add(filesend)
                print(file)
                email.attach(file.name, file.read())
            filepool.save()
            mail.files = filepool

        mail.save()

        mail.mailbox_key = mailbox_save(email, 'sendet1')
        try:
            email = mail.create_email()
            # mail.mailbox_key = mailbox_save(email)
            email.send()
            mail.status = "1"
            mail.logs.add(MessageLog.objects.log(mail, RESULT_SUCCESS))
            mail.date_send = datetime_now()
            mail.save()
            return corrent_mail(request, id=mail.id)

        except (socket_error, smtplib.SMTPSenderRefused,
                smtplib.SMTPRecipientsRefused,
                smtplib.SMTPDataError,
                smtplib.SMTPAuthenticationError) as err:
            mail.logs.add(MessageLog.objects.log(mail, RESULT_FAILURE, log_message=str(err)))
            mail.status = "4"

    return render(request, 'email_send_form.html', context={'adress': adress})


@login_required
def sendtest(request):
    send_all()

    return render(request, 'aftersendmail.html', context={'result': 'НЕ отправленно'})


@login_required
def email_add(request):
    msg = {'type': None,
           'text': None}

    if request.method == 'POST':
        zap = ZapEmailAdd.objects.create()
        zap.user = request.user
        zap.text = request.POST['text']
        zap.name = request.POST['name']
        zap.email_addres = request.POST['email_addres']
        msg['type'] = 'info'
        msg['text'] = f"Ваш запит на додавання {request.POST['email_addres']} в адресну книгу прийнято"
        zap.save()
        return render(request, 'ZapEmailadd.html', context={'msg': msg})


    return render(request, 'ZapEmailadd.html', context={'msg': None})


@login_required
def resend_email(request, id):
    mail = Mail.objects.get(id=id)
    msg = {'type': None,
           'text': None}
    try:
        email = mail.create_email()
        email.send()
        mail.status = "1"
        msg['type'] = 'alert-success'
        msg['text'] = 'Повідомлення успішно відправленно'
        log_msg = "користувач відправив повідомлення повторно"  # % request.POST.user.get_username()
        mail.logs.add(MessageLog.objects.log(mail, RESULT_SUCCESS, log_message=log_msg))
        mailbox_save(email, 'sendet1')
        mail.save()

    except (socket_error, smtplib.SMTPSenderRefused,
            smtplib.SMTPRecipientsRefused,
            smtplib.SMTPDataError,
            smtplib.SMTPAuthenticationError) as err:
        mail.logs.add(MessageLog.objects.log(mail, RESULT_FAILURE, log_message=str(err)))
        mail.status = "4"
        msg['type'] = 'alert-danger'
        msg['text'] = 'Під час відправки виникла помилка спробуйте пізніше'
        print(err)
        mailbox_save(email, 'sendet1')
    return email_lists(request, msg)


def test_html(request):
    i = [x for x in range(150)]

    return render(request, 'test_html.html', context={'i':i})


@login_required
def list_zap(request):
    zap = ZapEmailAdd.objects.filter(status='1')

    return render(request, 'list_zap.html', context={'zap': zap, 'msg':None})


@login_required
def email_add_accept(request, id=None):
    """
    обработка запроса на добовление почтового адреса пользователью
    если адрес существует ону будет добавен пользователю, в противном случае сначала сохраняеться запрашиваемый адрес
    после этого происходит проверка на наличие "групы" аресов для пользователя, если не существует будет создана,
    после чего в неё добавиться указаный адрес
    :param request:
    :param id:
    :return:
    """
    if request.user.get_username() == 'admin' and id is not None:
        zap = ZapEmailAdd.objects.get(id=id)
        email_addres, created = Email_addres.objects.get_or_create(addres=zap.email_addres)
        if created:
            email_addres.name = zap.name
            email_addres.save()

        grup_emails, created = GrupMail.objects.get_or_create(sender=zap.user)
        if created:
            grup_emails.name = zap.user.get_username()
            grup_emails.save()
        grup_emails.list_mails.add(email_addres)
        zap.status = '2'
        zap.save()

    return list_zap(request)


@login_required
def add_emails_to_grupe(request):

    users = User.objects.all()
    adress = Email_addres.objects.all()
    msg = None

    if request.method == 'POST':
        user = User.objects.get(id=int(request.POST['user']))
        email_addres = request.POST.getlist('addres')

        msg = {'type': 'info',
               'text': f'Користувачу {user.get_username()} доданно адреси:\n'}

        grup_emails, created = GrupMail.objects.get_or_create(sender=user)
        if created:
            grup_emails.name = user.get_username()
            grup_emails.save()

        if isinstance(email_addres, list):
            for adr in email_addres:
                addess_to_add = Email_addres.objects.get(id=int(adr))
                msg['text'] += ' ' + addess_to_add.addres
                grup_emails.list_mails.add(addess_to_add)

    return render(request, 'add_emails_to_grupe.html', context={'users': users, 'adress': adress, 'msg': msg})


def re_create_mail(request, id):
    if request.user.get_username() not in ['admin', 'Уколова']:
        try:
            adress = GrupMail.objects.get(sender=request.user).list_mails.all()
        except:
            adress = []
    else:
        adress = Email_addres.objects.all()

    mail = Mail.objects.get(id=id)
    re_mail = {"title": mail.title,
               "body": mail.body,
               "adress": mail.to.all()}

    return render(request, 'email_send_form.html', context={'adress': adress, "msg": re_mail})


def get_income_pop(request):
    pass


def list_incomeMail(request):
    """
    отображение всех подряд сообщений
    :param request:
    :return:
    """

    grup_mails = [addr.id for addr in list(GrupMail.objects.get(sender=request.user).list_mails.all())]

    def filter(query, word):
        return query.filter(Q(sender__addres__icontains=word) |
                            Q(sender__name__icontains=word) |
                            Q(to__icontains=word) |
                            Q(title__icontains=word) |
                            Q(body__icontains=word)).distinct()

    search_query = request.GET.get('search', '')
    page_query = request.GET.get('page', '')
    # если есть поисковый запрос
    if search_query:
        if request.user.get_username() not in ['admin', 'Уколова']:
            mails = IncomeMail.objects.filter(sender__in=grup_mails).order_by('-data_income')
        else:
            mails = IncomeMail.objects.all().order_by('-data_income')
        for word in search_query.split():

            mails = filter(mails, word)
        paginator = Paginator(mails, 15)
        page = request.GET.get('page')

    # в отсальных случаях
    else:
        if request.user.get_username() not in ['admin', 'Уколова']:
            mails = IncomeMail.objects.filter(sender__in=grup_mails).order_by('-data_income')
        else:
            mails = IncomeMail.objects.all().order_by('-data_income')
        paginator = Paginator(mails, 15)
        page = request.GET.get('page')

    try:
        mails = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mails = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mails = paginator.page(paginator.num_pages)
    pages = []
    if paginator.num_pages <= 5:
        pages = [x for x in paginator.page_range]
    elif mails.number:
        for x in paginator.page_range:
            if mails.number - 5 < x < mails.number + 5:
                pages.append(x)

    return render(request, template_name="list_income_mails.html", context={"mails": mails,
                                                                            "search_query": search_query})


def get_corrent_incomMail(request, id):
    """
    отображение конкретного отправления
    :param request:
    :param id:
    :return:
    """
    incomeMail = get_object_or_404(IncomeMail, id=id)
    return render(request, template_name="corrent_incom_mail.html", context={"mail": incomeMail})

