from django.urls import path

from . import views

urlpatterns = [
 path('<int:pk>/', views.VeureUsuariView.as_view(), name='usuari'),
 path('perfil/', views.EditarPerfilView.as_view(), name='perfil'),
 path('login/', views.LoginView.as_view(), name='login'),
 path('logout/', views.logout, name='logout'),
 path('registre/', views.RegistreView.as_view(), name='registre'),
]
