from __future__ import unicode_literals

from django.contrib import admin

from .models import MessageLog, Email_addres, FileSend, GrupMail, Mail, FilePool, ZapEmailAdd, IncomeMail, ExternalMailBox


class LogAdmin(admin.ModelAdmin):
    list_display = ["message_id", "when_added", "result","log_message"]


class MailAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'title']
    list_display_links = ['id', 'sender']
    list_filter = ['sender']
    search_fields = ['sender__username', 'title', 'to__addres']
    filter_horizontal = ["to", 'logs']


class ZapEmailAddAdmin(admin.ModelAdmin):

     def change_view(self, request, object_id, form_url='', extra_context=None):
         return self.changeform_view(request, object_id, form_url, extra_context)


class IncomeMailAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'title']
    list_display_links = ['id', 'sender']
    list_filter = ['sender']
    search_fields = ['title', 'sender__addres']



class GrupMailAdmin(admin.ModelAdmin):
    filter_horizontal = ["list_mails"]


class Email_addresAdmin(admin.ModelAdmin):
    search_fields = ['addres', 'name']
    list_display = ['addres', 'name']


#
admin.site.register(ZapEmailAdd, ZapEmailAddAdmin)

admin.site.register(MessageLog, LogAdmin)
admin.site.register(Email_addres, Email_addresAdmin)
admin.site.register(Mail, MailAdmin)
admin.site.register(FileSend)
admin.site.register(GrupMail, GrupMailAdmin)
admin.site.register(FilePool)
admin.site.register(IncomeMail, IncomeMailAdmin)
admin.site.register(ExternalMailBox)
