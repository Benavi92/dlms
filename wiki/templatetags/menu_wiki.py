from django import template
from wiki.models import ProgramComplex

register = template.Library()

@register.simple_tag(name='menu_wiki')
def menu_wiki():
    programs = ProgramComplex.objects.all()
    #programs = [program.name for program in ProgramComplex.objects.all()]
    shablon = '<div class="dropdown-menu" aria-labelledby="navbarDropdown">' \
              '<a class="dropdown-item" href="/wiki/program/%s">%s</a>' \
              '        <div class="dropdown-divider"></div>'
    menu = ""
    for program in programs:
        menu += shablon % (program.name, program.name)


    return menu