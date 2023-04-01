from django.contrib.auth import authenticate, login as djangologin, logout as djangologout
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, FormView
from .forms import LoginForm
from .models import Usuari


class VeureUsuariView(TemplateView):
    template_name = 'usuaris_perfil.html'


class LoginView(FormView):
    template_name = 'usuaris_login.html'
    form_class = LoginForm
    success_url = reverse_lazy('tots_issues')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Comprovem que és un usuari nostre (per username o email)
            try:
                Usuari.objects.get(user__username=username)
            except Usuari.DoesNotExist:
                try:
                    usuari = Usuari.objects.get(user__email=username)
                    username = usuari.user.username
                except Usuari.DoesNotExist:
                    form.add_error(None, _('No existeix un usuari amb aquest username o email'))
                    return render(request, self.template_name, {'form': form})

            # Autentiquem l'usuari (Django)
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                djangologin(request, user)
                return redirect(self.success_url)
            else:
                form.add_error(None, _('Usuari o contrasenya incorrectes'))
        else:
            form = LoginForm()
        return render(request, self.template_name, {'form': form})
