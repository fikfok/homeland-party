from django import forms
from django.forms import EmailInput


class InviteForm(forms.Form):
    email = forms.EmailField(widget=EmailInput(attrs={'placeholder': "Email: email@domain.com"}))
