from django import forms
from django.forms import EmailInput


class InviteForm(forms.Form):
    email = forms.EmailField(
        widget=EmailInput(attrs={'placeholder': "Email: email@domain.com", 'class': 'form-control'})
    )


class CustomSetPasswordForm(forms.Form):
    PASSWORD_MIN_LEN = 6

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        self._check_password(psw=password1)
        return password1

    def clean_new_password2(self):
        password2 = self.cleaned_data.get('new_password2')
        self._check_password(psw=password2)
        return password2

    def clean(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')

    def _check_password(self, psw: str):
        if len(psw) < self.PASSWORD_MIN_LEN:
            raise forms.ValidationError(f'Пароль должен быть не менее {self.PASSWORD_MIN_LEN} символов')
