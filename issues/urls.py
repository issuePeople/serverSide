from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.CrearIssueView.as_view(), name='crear_issue'),
    path('list/', views.ListIssueView.as_view(), name='tots_issues'),
]
