from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from mailer.models import Mail
from dfs_exch.models import DfsZap
from .serializers import MailSerializer, DFSSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class MailView(APIView):
    # базовый вариант требования авторизаций
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request, id=None):
        if id is None:
            mails = Mail.objects.all()
            many = True
        else:
            mails = Mail.objects.get(id=id)
            many = False

        serializer = MailSerializer(mails, many=many)
        return Response({"mails": serializer.data})


# Create your views here.
class DfsView(APIView):
    # базовый вариант требования авторизаций
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return DfsZap.objects.get(pk=pk)
        except DfsZap.DoesNotExist:
            raise Http404

    def get(self, request, id=None):
        if id is None:
            zap = DfsZap.objects.all()
            many = True
        else:
            zap = DfsZap.objects.get(num=id)
            many = False

        serializer = DFSSerializer(zap, many=many)
        return Response({"DfsZap": serializer.data})

    def post(self, request, format=None):
        serializer = DFSSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
