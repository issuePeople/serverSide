from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, mixins, status
from rest_framework.response import Response
from issues.models import Issue, Tag
from usuaris.models import Usuari
from . import serializers


class IssuesView(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    models = Issue
    serializer_class = serializers.IssueSerializer

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

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'create':
            # Quan fem get d'un issue concret n'obtenim tota la informació
            return serializers.IssueExtendedSerializer
        else:
            # En el list tenim només la info bàsica
            # En els updates també podem modificar només la informació bàsica
            return self.serializer_class

    def create(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.POST['creador_id'] = request.user
        response = super().create(request)
        request.POST._mutable = False
        return response


class ObservadorsView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Usuari.objects.all()
    serializer_class = serializers.UsuariSerializer

    def get_queryset(self):
        # Aconseguim l'issue donat per paràmetre
        issue_id = self.kwargs['issue_id']
        issue = get_object_or_404(Issue, id=issue_id)

        # Filtrem per obtenir només els observadors de l'issue
        queryset = super().get_queryset()
        queryset = queryset.filter(observats=issue)
        return queryset

    def create(self, request, *args, **kwargs):
        # Per paràmetre ens ha de venir l'observador a afegir
        id_observador = request.data.get('observador', None)
        if id_observador:
            # Busquem l'usuari i l'issue que hem de relacionar
            usuari = get_object_or_404(Usuari, user_id=id_observador)
            issue_id = self.kwargs['issue_id']
            issue = get_object_or_404(Issue, id=issue_id)

            # Guardem la relació
            issue.observadors.add(usuari)
            issue.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'error': "Has d'indicar l'identificador de l'observador a afegir"})

    def destroy(self, request, *args, **kwargs):
        # Tindrem /issues/issue_id/observadors/pk: Agafem els paràmetres, l'issue i l'usuari
        id_observador = kwargs.get('pk')
        usuari = get_object_or_404(Usuari, user_id=id_observador)
        id_issue = kwargs.get('issue_id')
        issue = get_object_or_404(Issue, id=id_issue)

        # Esborrem la relació entre issue i observador
        issue.observadors.remove(usuari)
        issue.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsIssueView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        # Aconseguim l'issue donat per paràmetre
        issue_id = self.kwargs['issue_id']
        issue = get_object_or_404(Issue, id=issue_id)

        # Filtrem per obtenir només els tags d'aquell issue
        queryset = super().get_queryset()
        queryset = queryset.filter(issues=issue)
        return queryset

    def create(self, request, *args, **kwargs):
        # Per paràmetre ens ha de venir el nom i color del tag a afegir
        nom = request.data.get('nom', None)
        color = request.data.get('color', None)
        if nom and color:
            # Busquem el tag a afegir (si no existeix, el creem) i l'issue que hem de relacionar
            tag, created = Tag.objects.get_or_create(nom=nom, defaults={'color': color})
            issue_id = self.kwargs['issue_id']
            issue = get_object_or_404(Issue, id=issue_id)

            # Guardem la relació
            issue.tags.add(tag)
            issue.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'error': "Has d'indicar l'identificador de l'observador a afegir"})

    def destroy(self, request, *args, **kwargs):
        # Tindrem /issues/issue_id/tags/pk: Agafem els paràmetres, l'issue i del tag
        nom_tag = kwargs.get('pk')
        tag = get_object_or_404(Tag, nom=nom_tag)
        id_issue = kwargs.get('issue_id')
        issue = get_object_or_404(Issue, id=id_issue)

        # Esborrem la relació entre issue i observador
        issue.tags.remove(tag)
        issue.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsuarisView(viewsets.ModelViewSet):
    queryset = Usuari.objects.all()
    models = Usuari
    serializer_class = serializers.UsuariSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            # Quan fem get d'un usuari concret n'obtenim tota la informació
            return serializers.UsuariExtendedSerializer
        else:
            # En el list tenim només la info bàsica
            # En els updates també podem modificar només la informació bàsica
            return self.serializer_class
