import os
import uuid
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(name='setting_email')
def setting_email():
    return str(settings.EMAIL_HOST_USER)
