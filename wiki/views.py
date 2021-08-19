from django.shortcuts import render
from .models import Update, ProgramComplex

# Create your views here.


def correntprogram(request, program):
    updates = Update.objects.filter(programComplex__name=program)
    #programs = ProgramComplex.objects.all()

    return render(request, "wiki\\correntprogram.html", context={"updates": updates})


def main(request):
    programs = ProgramComplex.objects.all()
    return render(request, "wiki\\main.html", context={"programs": programs})


def correntupdate(request, program, id):
    update = Update.objects.get(id=id)
    return render(request, "wiki\\correntupdate.html", context={"update": update})

