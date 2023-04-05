from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListIssueView.as_view(), name='tots_issues'),
    path('create/', views.CrearIssueView.as_view(), name='crear_issue'),
    path('bulk/', views.CrearBulkView.as_view(), name='bulk_issue'),
    path('<int:id>/edit/', views.EditarIssueView.as_view(), name='editar_issue'),
    path('<int:id>/delete/', views.EsborrarIssueView.as_view(), name='esborrar_issue'),
    path('attachments/<int:id>/delete/', views.EsborrarAttachmemtView.as_view(), name='esborrar_attachment'),
    path('<int:id_issue>/tags/<str:nom_tag>/delete/', views.EsborrarTagIssueView.as_view(), name='esborrar_tag_issue'),
    path('<int:id_issue>/assignacio/delete/', views.EsborrarAssignacioIssue.as_view(), name='esborrar_assignacio'),
    path('<int:id_issue>/observador/<int:id_usuari>/delete/', views.EsborrarObservadorIssue.as_view(), name='esborrar_observador'),
]
