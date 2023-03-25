from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.urls import reverse

# Create your views here.

class VeureUsuari(TemplateView):
    template_name = 'usuaris_perfil.html'