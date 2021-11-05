from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class Login(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/login.html'


class Logout(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/logout.html'


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordReset(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'user/password_reset_confirm.html'
