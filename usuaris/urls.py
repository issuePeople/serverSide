from django.urls import path

from . import views

urlpatterns = [
 path('perfil/', views.VeureUsuari.as_view(), name='tots_issues'), 
]
