import os
import uuid
from django import template
from django.conf import settings
from wiki.models import ProgramComplex

register = template.Library()

@register.simple_tag(name='cache_bust')
def cache_bust():

    if settings.DEBUG:
        version = uuid.uuid1()
    else:
        version = os.environ.get('PROJECT_VERSION')
        if version is None:
            version = '1'

    return '__v__={version}'.format(version=version)


@register.simple_tag(name='menu_wiki')
def menu_wiki():
    #programs = ProgramComplex.objects.all()
    programs = [program.name for program in ProgramComplex.objects.all()]

    return programs