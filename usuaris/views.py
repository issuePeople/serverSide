from django.contrib.auth import authenticate, login as djangologin, logout as djangologout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView, FormView
from rest_framework.authtoken.models import Token
from .forms import UsuariForm, LoginForm, RegistreForm
from issuePeople.mixins import IsAuthenticatedMixin
from issues.models import Log
from .models import Usuari
from issuePeople import settings


class VeureUsuariView(IsAuthenticatedMixin, DetailView):
    model = Usuari
    template_name = 'usuaris_info.html'
    context_object_name = 'usuari'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        queryset = Usuari.objects.all().prefetch_related('observats')
        return get_object_or_404(queryset, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_navbar(self.request))
        context.update({
            'logs': Log.objects.filter(usuari=self.get_object()).order_by('-data'),
            'usuaris': Usuari.objects.all(),
            'NO_AVATAR_URL': settings.NO_AVATAR_URL
        })
        return context


class EditarPerfilView(IsAuthenticatedMixin, UpdateView):
    model = Usuari
    template_name = 'usuaris_perfil.html'
    form_class = UsuariForm
    context_object_name = 'usuari'
    success_url = reverse_lazy('perfil')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_navbar(self.request))
        context.update({
            'usuaris': Usuari.objects.all()
        })
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Usuari.objects.all(), user=self.request.user)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if 'guardar_avatar' in request.POST:
                usuari = self.get_object()
                avatar = form.cleaned_data['avatar']
                usuari.avatar = avatar
                usuari.save()
            elif 'guardar_avatar_defecte' in request.POST:
                usuari = self.get_object()
                usuari.avatar = settings.DEFAULT_AVATAR
                usuari.save()
            elif 'guardar_info' in request.POST:
                usuari = self.get_object()
                username = form.cleaned_data['username']
                usuari.user.username = username
                email = form.cleaned_data['email']
                usuari.user.email = email
                first_name = form.cleaned_data['first_name']
                usuari.user.first_name = first_name
                usuari.user.save()
                bio = form.cleaned_data['bio']
                usuari.bio = bio
                usuari.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class LoginView(FormView):
    template_name = 'usuaris_login.html'
    form_class = LoginForm
    success_url = reverse_lazy('tots_issues')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'logo_url': settings.LOGO_JPG_URL,
        })
        return context

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
                    return render(request, self.template_name, {'form': form, 'logo_url': settings.LOGO_JPG_URL})

            # Autentiquem l'usuari (Django)
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                # Si no tenia token, li donem un
                Token.objects.get_or_create(user=user)
                djangologin(request, user)
                return redirect(self.success_url)
            else:
                form.add_error(None, _('Usuari o contrasenya incorrectes'))
        else:
            form = LoginForm()
        return render(request, self.template_name, {'form': form, 'logo_url': settings.LOGO_JPG_URL})


class RegistreView(LoginView):
    template_name = 'usuaris_singUp.html'
    form_class = RegistreForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'logo_url': settings.LOGO_JPG_URL,
        })
        return context

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

            # Ahhh, i li donem un token ara!
            Token.objects.create(user=user)

            # Fem login
            djangologin(request, user)
            return redirect(self.success_url)
        else:
            form = RegistreForm()
            return render(request, self.template_name, {'form': form, 'logo_url': settings.LOGO_JPG_URL})


def logout(request):
    djangologout(request)
    return redirect(reverse('login'))


def get_context_navbar(request):
    usuari, created = Usuari.objects.get_or_create(user=request.user)
    return {
        'logged_usuari': usuari,
        'logo_url': settings.LOGO_PNG_URL
    }
