from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, mixins, status
from rest_framework.response import Response
from issues.models import Issue, Tag, Comentari, Attachment, Log
from usuaris.models import Usuari
from . import serializers


def registrar_log_update(issue, usuari, tipus, previ, nou):
    if str(previ) != str(nou):
        Log.objects.create(
            issue=issue,
            usuari=usuari,
            tipus=tipus,
            valor_previ=previ,
            valor_nou=nou
        )


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

        # Registrem el log de la creació, si s'ha creat
        if response.status_code == status.HTTP_201_CREATED:
            Log.objects.create(
                issue=get_object_or_404(Issue, id=response.data['id']),
                usuari=request.user.usuari,
                tipus=Log.CREAR,
                valor_previ=None,
                valor_nou=None
            )
        return response

    def update(self, request, *args, **kwargs):
        issue_id = kwargs['pk']
        issue = get_object_or_404(Issue, id=issue_id)
        usuari = request.user.usuari

        response = super().update(request, args, kwargs)

        # Si s'han fet els updates, registrem els logs de canvis d'atributs
        if response.status_code == status.HTTP_200_OK:
            issue_nou = get_object_or_404(Issue, id=issue_id)

        for key in request.data.keys():
            if key == 'subject':
                registrar_log_update(issue, usuari, Log.SUBJ, issue.subject, issue_nou.subject)
            elif key == 'descripcio':
                registrar_log_update(issue, usuari, Log.DESCR, issue.descripcio, issue_nou.descripcio)
            elif key == 'tipus':
                registrar_log_update(issue, usuari, Log.TIPUS, issue.tipus, issue_nou.tipus)
            elif key == 'gravetat':
                registrar_log_update(issue, usuari, Log.GRAV, issue.gravetat, issue_nou.gravetat)
            elif key == 'prioritat':
                registrar_log_update(issue, usuari, Log.PRIO, issue.prioritat, issue_nou.prioritat)
            elif key == 'bloquejat':
                registrar_log_update(issue, usuari, Log.BLOQ, issue.bloquejat, issue_nou.bloquejat)
            elif key == 'dataLimit':
                if issue.dataLimit:
                    previ = issue.dataLimit.strftime("%d %b. %Y")
                else:
                    previ = 'Sense definir'
                if issue_nou.dataLimit:
                    nou = issue_nou.dataLimit.strftime("%d %b. %Y")
                else:
                    nou = 'Sense definir'
                registrar_log_update(issue, usuari, Log.LIMIT, previ, nou)

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
                'error': "Has d'indicar el nom i el color del tag a afegir"})

    def destroy(self, request, *args, **kwargs):
        # Tindrem /issues/issue_id/tags/pk: Agafem els paràmetres, l'issue i del tag
        nom_tag = kwargs.get('pk')
        tag = get_object_or_404(Tag, nom=nom_tag)
        id_issue = kwargs.get('issue_id')
        issue = get_object_or_404(Issue, id=id_issue)

        # Esborrem la relació entre issue i tag
        issue.tags.remove(tag)
        issue.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ComentarisView(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Comentari.objects.all()
    serializer_class = serializers.ComentariSerializer

    def get_queryset(self):
        # Aconseguim l'issue donat per paràmetre
        issue_id = self.kwargs['issue_id']
        issue = get_object_or_404(Issue, id=issue_id)

        # Filtrem per obtenir només els comentaris d'aquell issue
        queryset = super().get_queryset()
        queryset = queryset.filter(issue=issue)
        queryset = queryset.order_by('-data')
        return queryset

    def create(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.POST['autor_id'] = request.user
        request.POST['issue_id'] = kwargs['issue_id']
        response = super().create(request)
        request.POST._mutable = False
        return response


class AttachmentsView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Attachment.objects.all()
    serializer_class = serializers.AttachmentSerializer

    def get_queryset(self):
        # Aconseguim l'issue donat per paràmetre
        issue_id = self.kwargs['issue_id']
        issue = get_object_or_404(Issue, id=issue_id)

        # Filtrem per obtenir només els attachments d'aquell issue
        queryset = super().get_queryset()
        queryset = queryset.filter(issue=issue)
        queryset = queryset.order_by('-data')
        return queryset

    def create(self, request, *args, **kwargs):
        # Quan fem multipart post, no podem fer mutable la request, així que fem override de
        # tot el create per forçar el issue_id rebut per kwargs
        data = request.data.copy()
        data.update({'issue_id': kwargs['issue_id']})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Si arribem aquí és que s'ha afegit l'attachment, així que escrivim el log
        Log.objects.create(
            issue=get_object_or_404(Issue, id=kwargs['issue_id']),
            usuari=request.user.usuari,
            tipus=Log.ADD_ATT,
            valor_nou=get_object_or_404(Attachment, id=serializer.data['id']).document.name
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        # Agafem el nom de l'attachment per després poder crear el log
        valor_previ = self.get_object().document.name

        # Fem el destroy
        response = super().destroy(request, args, kwargs)

        # Si s'ha destruit correactament, registrem el log
        if response.status_code == status.HTTP_204_NO_CONTENT:
            Log.objects.create(
                issue=get_object_or_404(Issue, id=kwargs['issue_id']),
                usuari=request.user.usuari,
                tipus=Log.DEL_ATT,
                valor_previ=valor_previ
            )

        return response


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
