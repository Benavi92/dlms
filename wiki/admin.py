from django.contrib import admin
from .models import FileUpdate, ProgramComplex, Update, Tag

# Register your models here.

admin.site.register(FileUpdate)
admin.site.register(ProgramComplex)
admin.site.register(Update)
admin.site.register(Tag)
