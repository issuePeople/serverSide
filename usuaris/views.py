from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.urls import reverse

# Create your views here.


class VeureUsuariView(TemplateView):
    template_name = 'usuaris_perfil.html'


class LoginView(TemplateView):
    template_name = 'usuaris_login.html'
