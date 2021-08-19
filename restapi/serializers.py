from rest_framework import serializers
from mailer.models import Mail, Email_addres, FilePool, FileSend, MessageLog
from django.contrib.auth.models import User
from dfs_exch.models import DfsZap



class UsernameSerializer(serializers.ModelSerializer):
    """docstring for LogMassageSerializer."""
    class Meta:
        model = User
        fields = ("username",)


class LogMassageSerializer(serializers.ModelSerializer):
    """docstring for LogMassageSerializer."""
    class Meta:
        model = MessageLog
        fields = ("message_id", "when_attempted", "result", "log_message")


class EmailAddresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email_addres
        fields = ("addres",)


class FileSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileSend
        fields = ("name", "url")


class FilePoolSerializer(serializers.ModelSerializer):
    files = FileSendSerializer(read_only=True, many=True)

    class Meta:
        model = FilePool
        fields = ("files",  )

class MailSerializer(serializers.ModelSerializer):
    to = EmailAddresSerializer(read_only=True, many=True)
    files = FilePoolSerializer(read_only=True)
    logs = LogMassageSerializer(read_only=True, many=True)
    sender = UsernameSerializer(read_only=True)

    class Meta:
        model = Mail
        fields = ("id", "to", "date_send", "title", "body", "status", "files", "logs", "sender")


####################################################################################################
# DFS MODULE
####################################################################################################

class DFSSerializer(serializers.ModelSerializer):
    class Meta:
        model = DfsZap
        fields = ("numb", "program", "date_in", "name", "path")