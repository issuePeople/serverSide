from django.urls import path

from . import views

urlpatterns = [
    path('', views.ListIssueView.as_view(), name='tots_issues'),
    path('create/', views.CrearIssueView.as_view(), name='crear_issue'),
]
