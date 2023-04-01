from django.urls import path

from . import views

urlpatterns = [
 path('perfil/', views.VeureUsuariView.as_view(), name='perfil'),
 path('login/', views.LoginView.as_view(), name='login'),
 path('logout/', views.logout, name='logout'),
]
