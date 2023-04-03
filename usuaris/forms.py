from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import Usuari


class UsuariForm(UserChangeForm):
    class Meta:
        model = Usuari
        fields = ('bio',)


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)


class RegistreForm(LoginForm):
    password2 = forms.CharField(required=True, widget=forms.PasswordInput)
    email = forms.CharField(required=True)
    name = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password2'):
            self.add_error(None, _('Les contrasenyes no coincideixen!'))
        return cleaned_data

    def crear_usuari(self):
        # Primer creem l'usuari de Django
        user = User(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('nom'),
        )
        # Encripta la contrasenya
        user.set_password(self.cleaned_data.get('password'))
        user.save()

        # Per últim, el nostre usuari, enllaçat amb el Django
        usuari = Usuari(
            user=user
        )
        usuari.save()
        return usuari

