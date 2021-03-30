from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.template import RequestContext
from django.views import generic

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm


class HomePage(LoginRequiredMixin, generic.TemplateView, RequestContext):
    login_url = '/login'
    template_name = 'home.html'


class LoginPage(generic.TemplateView):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = self._authenticate(email=cleaned_data['email'], password=cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    return HttpResponse('Аккаунт заблокирован')
            else:
                return HttpResponse('Неверный логин')
        else:
            return HttpResponse('Неверная дата')

    def _authenticate(self, email: str, password: str):
        default_user = None
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = default_user
        else:
            if not user.check_password(password):
                user = default_user
        return user
