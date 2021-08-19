from django.db import models

# Create your models here.

STATUS_CODES = (("1", "Актуальний"),
                ("2", "замінений"))


class ProgramComplex(models.Model):
    name = models.CharField(max_length=125)

    def __str__(self):
        return "{0}".format(self.name)


class Tag(models.Model):
    programComplex = models.ForeignKey(ProgramComplex, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=150)


class Update(models.Model):
    programComplex = models.ForeignKey(ProgramComplex, on_delete=models.DO_NOTHING)
    num = models.IntegerField(null=False)
    prefix = models.CharField(max_length=30, blank=True, null=True)
    style = models.TextField(blank=True)
    text = models.TextField(blank=True)

    date_install = models.DateField(auto_now=True)
    date_income = models.DateField(auto_now=True)

    tags = models.ManyToManyField(Tag)


class FileUpdate(models.Model):
    file = models.CharField(max_length=256)
    path_file = models.CharField(max_length=256, blank=True)
    dateCreate = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1,
                              choices=STATUS_CODES,
                              default="1")
    version = models.ForeignKey(Update, on_delete=models.DO_NOTHING)



