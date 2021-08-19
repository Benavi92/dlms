from django import forms
from .models import Mail


class EmailMassageForm(forms.ModelForm):
    to = forms.ModelMultipleChoiceField(queryset=None)
    title = forms.CharField(label="тема")
    body = forms.CharField(label="тело")

    class Meta:
        model = Mail
        fields = ('title', 'to', 'body')
