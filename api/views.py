from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions
from issues.models import Issue
from usuaris.models import Usuari
from . import serializers


class IssuesView(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    models = Issue
    serializer_class = serializers.IssueExtendedSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'id': ['exact', 'in'],
        'tipus': ['exact', 'in'],
        'estat': ['exact', 'in'],
        'gravetat': ['exact', 'in'],
        'prioritat': ['exact', 'in'],
        'assignacio__user__id': ['exact', 'in'],
        'observadors__user__id': ['exact', 'in'],
        'creador__user__id': ['exact', 'in'],
        'tags__nom': ['exact', 'in'],
    }
    ordering_fields = ['id', 'subject', 'descripcio', 'tipus', 'estat', 'gravetat',
                       'bloquejat', 'dataCreacio', 'dataLimit', 'dataModificacio',
                       'prioritat', 'assignacio', 'observadors', 'creador', 'tags']
    search_fields = ['subject', 'descripcio']


class UsuarisView(viewsets.ModelViewSet):
    queryset = Usuari.objects.all()
    models = Usuari
    serializer_class = serializers.UsuariExtendedSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            # Quan fem get obtenim tota la informació
            return serializers.UsuariExtendedSerializer
        else:
            # En el list tenim només la info bàsica
            # En els updates també podem modificar només la informació bàsica
            return serializers.UsuariSerializer
