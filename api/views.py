from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, mixins, status, permissions, parsers
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
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

    @swagger_auto_schema(
        responses={
            201: openapi.Response("", serializers.IssueExtendedSerializer),
            400: openapi.Response("Hi ha algun error en els valors donats per crear l'issue"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
        }
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Posem les dades del creador
        data['creador_id'] = request.user

        # Creem l'issue
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Registrem el log de la creació, si s'ha creat
        Log.objects.create(
            issue=get_object_or_404(Issue, id=serializer.data['id']),
            usuari=request.user.usuari,
            tipus=Log.CREAR,
            valor_previ=None,
            valor_nou=None
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'])
    @swagger_auto_schema(
        responses={
            201: openapi.Response("Es creen els issues amb els valors donats", serializers.IssueSerializer),
            400: openapi.Response("Hi ha algun error en els valors donats per crear els issues"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
        }
    )
    def bulk(self, request):
        # Creem els issues amb el serializer
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        issues = serializer.save()  # Guarda i aconseguim els issues creats

        # Posem el creador i registrem els log de la creació, si s'han creat
        for issue in issues:
            issue.creador = request.user.usuari
            issue.save()

            Log.objects.create(
                issue=issue,
                usuari=request.user.usuari,
                tipus=Log.CREAR,
                valor_previ=None,
                valor_nou=None
            )

        # Retornem les dades dels issues creats
        serialized_data = serializers.IssueSerializer(issues, many=True).data
        return Response(serialized_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("", serializers.IssueExtendedSerializer),
            404: openapi.Response("No hi ha cap issue amb l'identificador donat"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("", serializers.IssueSerializer),
            400: openapi.Response("Hi ha algun error en els valors donats per actualitzar l'issue"),
            404: openapi.Response("No hi ha cap issue amb l'identificador donat"),
        }
    )
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
            elif key == 'assignacio_id':
                if issue.assignacio:
                    previ = issue.assignacio.user.first_name
                else:
                    previ = 'Sense assignar'
                if issue_nou.assignacio:
                    nou = issue_nou.assignacio.user.first_name
                else:
                    nou = 'Sense assignar'
                registrar_log_update(issue, usuari, Log.ASSIGN, previ, nou)

        return response

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            204: openapi.Response("S'esborra l'issue correctament"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            404: openapi.Response("No hi ha cap issue amb l'identificador donat"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, args, kwargs)


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

    @swagger_auto_schema(
        responses={
            200: openapi.Response("", serializers.UsuariSerializer),
            404: openapi.Response("No existeix cap issue amb l'identificador donat")
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            201: openapi.Response("S'afegeix correctament l'observador a l'issue"),
            400: openapi.Response("No es dona el camp 'observador' a data"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            404: openapi.Response("No es troba l'issue o l'observador que es volen enllaçar"),
            409: openapi.Response("L'usuari que es vol posar d'observador de l'issue ja ho és"),
        }
    )
    def create(self, request, *args, **kwargs):
        # Per paràmetre ens ha de venir l'observador a afegir
        id_observador = request.data.get('observador', None)
        if id_observador:
            # Busquem l'usuari i l'issue que hem de relacionar
            usuari = get_object_or_404(Usuari, user_id=id_observador)
            issue_id = self.kwargs['issue_id']
            issue = get_object_or_404(Issue, id=issue_id)

            # Si l'usuari ja observa l'issue, llencem error
            if issue.observadors.contains(usuari):
                return Response(status=status.HTTP_409_CONFLICT, data={
                    'error': "L'usuari " + id_observador + " ja és observador de l'issue " + issue_id})

            # En cas que no, guardem la relació
            else:
                issue.observadors.add(usuari)
                issue.save()
                return Response(status=status.HTTP_201_CREATED, data={
                    'observador afegit': "S'ha afegit l'observador " + id_observador + " a l'issue " + issue_id})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'error': "Has d'indicar l'identificador de l'observador a afegir"})

    @swagger_auto_schema(
        responses={
            204: openapi.Response("S'esborra correctament la relació entre l'observador i l'issue"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            404: openapi.Response("No es troba l'issue o l'observador que es volen desenllaçar, o bé la relació no existia"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        # Tindrem /issues/issue_id/observadors/pk: Agafem els paràmetres, l'issue i l'usuari
        id_observador = kwargs.get('pk')
        usuari = get_object_or_404(Usuari, user_id=id_observador)
        id_issue = kwargs.get('issue_id')
        issue = get_object_or_404(Issue, id=id_issue)

        # Esborrem la relació entre issue i observador si l'usuari és observador
        if issue.observadors.contains(usuari):
            issue.observadors.remove(usuari)
            issue.save()
            return Response(status=status.HTTP_204_NO_CONTENT, data={
                'observador esborrat': "S'ha eliminat l'observador " + id_observador + " de l'issue " + id_issue})

        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={
                'error': "L'usuari " + id_observador + " no és observador de l'issue " + id_issue})


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

    @swagger_auto_schema(
        responses={
            200: openapi.Response("", serializers.TagSerializer),
            404: openapi.Response("No existeix cap issue amb l'identificador donat")
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            201: openapi.Response("S'afegeix correctament el tag a l'issue", serializer_class=None),
            400: openapi.Response("No es donen els camps nom i/o color a data"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            404: openapi.Response("No es troba l'issue a què se li vol afegir el tag"),
            409: openapi.Response("El tag que es vol afegir a l'issue ja està registrat en aquest issue"),
        }
    )
    def create(self, request, *args, **kwargs):
        # Per paràmetre ens ha de venir el nom i color del tag a afegir
        nom = request.data.get('nom', None)
        color = request.data.get('color', None)
        if nom and color:
            # Busquem el tag a afegir (si no existeix, el creem) i l'issue que hem de relacionar
            tag, created = Tag.objects.get_or_create(nom=nom, defaults={'color': color})
            issue_id = self.kwargs['issue_id']
            issue = get_object_or_404(Issue, id=issue_id)

            # Si l'issue ja tenia el tag, llencem error
            if issue.tags.contains(tag):
                return Response(status=status.HTTP_409_CONFLICT, data={
                    'error': "L'issue " + issue_id + " ja té el tag " + nom})

            # En cas que no, guardem la relació i registrem el log
            else:
                issue.tags.add(tag)
                issue.save()

                # Registrem el log
                Log.objects.create(
                    issue=issue,
                    usuari=request.user.usuari,
                    tipus=Log.ADD_TAG,
                    valor_nou=tag.nom
                )

                return Response(status=status.HTTP_201_CREATED, data={
                    'tag afegit': "S'ha afegit el tag " + nom + " a l'issue " + issue_id})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'error': "Has d'indicar el nom i el color del tag a afegir"})

    @swagger_auto_schema(
        responses={
            204: openapi.Response("S'esborra correctament la relació entre el tag i l'issue"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            404: openapi.Response("No es troba l'issue o el tag que es volen desenllaçar, o bé la relació no existia"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        # Tindrem /issues/issue_id/tags/pk: Agafem els paràmetres, l'issue i del tag
        nom_tag = kwargs.get('pk')
        tag = get_object_or_404(Tag, nom=nom_tag)
        id_issue = kwargs.get('issue_id')
        issue = get_object_or_404(Issue, id=id_issue)

        # Esborrem la relació entre issue i tag si l'issue té aquell tag
        if issue.tags.contains(tag):
            issue.tags.remove(tag)
            issue.save()

            # Registrem el log
            Log.objects.create(
                issue=issue,
                usuari=request.user.usuari,
                tipus=Log.DEL_TAG,
                valor_previ=tag.nom
            )

            return Response(status=status.HTTP_204_NO_CONTENT, data={
                'tag esborrat': "S'ha eliminat el tag " + nom_tag + " de l'issue " + id_issue})

        # Si l'issue no tenia el tag, llencem error
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={
                'error': "L'issue " + id_issue + " no té el tag " + nom_tag})


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

    @swagger_auto_schema(
        responses={
            200: openapi.Response("", serializers.ComentariSerializer),
            404: openapi.Response("No existeix cap issue amb l'identificador donat")
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            201: openapi.Response("Es crea correctament el comentari", serializers.ComentariSerializer),
            400: openapi.Response("No es dona el camp text del comentari a data"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            404: openapi.Response("No es troba l'issue a què se li vol afegir el comentari"),
        }
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Posem les dades de l'autor i de l'issue
        data['autor_id'] = request.user
        data['issue_id'] = kwargs['issue_id']

        # Creem el comentari
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AttachmentsView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Attachment.objects.all()
    serializer_class = serializers.AttachmentSerializer
    parser_classes = (parsers.MultiPartParser, )

    def get_queryset(self):
        # Aconseguim l'issue donat per paràmetre
        issue_id = self.kwargs['issue_id']
        issue = get_object_or_404(Issue, id=issue_id)

        # Filtrem per obtenir només els attachments d'aquell issue
        queryset = super().get_queryset()
        queryset = queryset.filter(issue=issue)
        queryset = queryset.order_by('-data')
        return queryset

    @swagger_auto_schema(
        responses={
            200: openapi.Response("", serializers.AttachmentSerializer),
            404: openapi.Response("No existeix cap issue amb l'identificador donat")
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('issue_id', openapi.IN_PATH, required=True, type=openapi.TYPE_INTEGER),
            openapi.Parameter('document', openapi.IN_FORM, required=True, type=openapi.TYPE_FILE),
        ],
        responses={
            201: openapi.Response("S'afegeix correctament l'attachment a l'issue", serializers.AttachmentSerializer),
            400: openapi.Response("No es dona el camp 'document' a data"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            404: openapi.Response("No es troba l'issue a què se li vol afegir l'attachment"),
            409: openapi.Response("El tag que es vol afegir a l'issue ja està registrat en aquest issue"),
        }
    )
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

    @swagger_auto_schema(
        responses={
            204: openapi.Response("S'esborra correctament l'attachment"),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            404: openapi.Response("No es troba l'issue o l'attachment donats"),
        }
    )
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


class LogsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Log.objects.all()
    serializer_class = serializers.LogSerializer

    def get_queryset(self):
        # Aconseguim l'issue donat per paràmetre
        issue_id = self.kwargs['issue_id']
        issue = get_object_or_404(Issue, id=issue_id)

        # Filtrem per obtenir només els logs d'aquell issue
        queryset = super().get_queryset()
        queryset = queryset.filter(issue=issue)
        queryset = queryset.order_by('-data')
        return queryset

    @swagger_auto_schema(
        responses={
            200: openapi.Response("", serializers.LogSerializer),
            404: openapi.Response("No existeix cap issue amb l'identificador donat")
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)


class UsuarisView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Usuari.objects.all()
    models = Usuari
    serializer_class = serializers.UsuariSerializer
    parser_classes = (parsers.MultiPartParser, )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            # Quan fem get d'un usuari concret n'obtenim tota la informació

            # Si estem consultant la nostra informació, rebem també el token:
            if self.kwargs.get('pk') == str(self.request.user.id):
                return serializers.UsuariWithTokenSerializer

            # Si no, veurem tota la informació però sense el token
            else:
                return serializers.UsuariExtendedSerializer
        else:
            # En el list tenim només la info bàsica
            # En els updates també podem modificar només la informació bàsica
            return self.serializer_class

    def check_object_permissions(self, request, obj):
        if request.method not in permissions.SAFE_METHODS and request.user.usuari != obj:
            raise PermissionDenied("No tens permís per executar aquesta acció.")

    @swagger_auto_schema(
        responses={
            200: openapi.Response("", serializers.UsuariExtendedSerializer),
            404: openapi.Response("No hi ha cap usuari amb l'identificador donat"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, args, kwargs)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('avatar', openapi.IN_FORM, required=False, type=openapi.TYPE_FILE),
        ],
        responses={
            200: openapi.Response("Modificacions aplicades correctament", serializers.UsuariSerializer),
            401: openapi.Response("Error d'autenticació: no es dona el token o és incorrecte"),
            403: openapi.Response("Error d'autenticació: s'intenta editar un usuari que no és un mateix/a"),
            404: openapi.Response("No hi ha cap usuari amb l'identificador donat"),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, args, kwargs)

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, args, kwargs)


class TagsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    models = Tag
    serializer_class = serializers.TagExtendedSerializer
