from django.contrib.auth import authenticate, login as djangologin, logout as djangologout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView, FormView
from .forms import UsuariForm, LoginForm, RegistreForm
from issuePeople.mixins import IsAuthenticatedMixin
from .models import Usuari


class VeureUsuariView(IsAuthenticatedMixin, DetailView):
    model = Usuari
    template_name = 'usuaris_info.html'
    context_object_name = 'usuari'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        queryset = Usuari.objects.all()
        return get_object_or_404(queryset, pk=pk)


class EditarPerfilView(IsAuthenticatedMixin, UpdateView):
    model = Usuari
    template_name = 'usuaris_perfil.html'
    form_class = UsuariForm
    context_object_name = 'usuari'
    success_url = reverse_lazy('perfil')

    def get_object(self, queryset=None):
        return get_object_or_404(Usuari.objects.all(), user=self.request.user)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if 'guardar_bio' in request.POST:
                bio = form.cleaned_data['bio']
                usuari = self.get_object()
                usuari.bio = bio
                usuari.save()
                return redirect(self.success_url)
        else:
            return self.form_invalid(form)


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


class RegistreView(LoginView):
    template_name = 'usuaris_singUp.html'
    form_class = RegistreForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            # Primer creem l'usuari de Django
            user = User(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                first_name=form.cleaned_data.get('name'),
            )
            # Encripta la contrasenya
            user.set_password(form.cleaned_data.get('password'))
            user.save()

            # Per últim, el nostre usuari, enllaçat amb el Django
            usuari = Usuari(
                user=user
            )
            usuari.save()

            # Fem login
            djangologin(request, user)
            return redirect(self.success_url)
        else:
            form = RegistreForm()
            return render(request, self.template_name, {'form': form})


def logout(request):
    djangologout(request)
    return redirect(reverse('login'))
