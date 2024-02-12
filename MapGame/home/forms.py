from django import forms

class CommandForm(forms.Form):
    command = forms.CharField(label='Command', max_length=255)
