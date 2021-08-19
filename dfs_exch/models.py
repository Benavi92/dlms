from django.db import models

# Create your models here.


class DfsZap(models.Model):
    numb = models.IntegerField(verbose_name="номер")
    program = models.CharField(blank=True, null=True, max_length=50)
    date_in = models.DateTimeField(auto_now=True)
    name = models.TextField(blank=True, null=True)
    path = models.CharField(blank=True, null=True, max_length=250)


