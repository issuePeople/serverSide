from django.views.generic import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View
from django_filters.views import FilterView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from issuePeople.mixins import IsAuthenticatedMixin
from .models import Issue, Tag, Attachment, Log
from .forms import IssueForm, IssueBulkForm, AttachmentForm, ComentariForm, TagForm
from usuaris.models import Usuari
from usuaris.views import get_context_navbar
from .filters import IssueFilter


class ListIssueView(IsAuthenticatedMixin, FilterView):
    model = Issue
    template_name = 'issue_list.html'
    filterset_class = IssueFilter
    context_object_name = 'issues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(Issue.get_types(self))
        context.update(get_context_navbar(self.request))
        context.update({
            'usuaris': Usuari.objects.all(),
            'tags': Tag.objects.all(),
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrem fent servir l'IssueFilter (fitlers.py)
        filter = IssueFilter(self.request.GET, queryset=queryset)

        # Ordenem a partir del paràmetre order_by (per defecte, ordenat x data creació)
        order_by = self.request.GET.get('order_by', '-dataCreacio')
        queryset = filter.qs.order_by(order_by)

        return queryset


class CrearIssueView(IsAuthenticatedMixin, CreateView):
    model = Issue
    template_name = 'issue_form.html'
    form_class = IssueForm
    success_url = reverse_lazy('tots_issues')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(Issue.get_types(self))
        context.update({
            'usuaris': Usuari.objects.all(),
        })
        return context

    def form_valid(self, form):
        # Especifiquem el creador de l'issue
        form.instance.creador = Usuari.objects.get(user=self.request.user)
        issue = form.save()
        log = Log(
            issue=issue,
            usuari=issue.creador,
            tipus=Log.CREAR
        )
        log.save()
        return redirect(self.success_url)


class EditarIssueView(IsAuthenticatedMixin, UpdateView):
    model = Issue
    template_name = 'issue_edit.html'
    form_class = IssueForm
    success_url = None
    context_object_name = 'issue'

    def get_object(self, queryset=None):
        id = self.kwargs.get('id')
        queryset = Issue.objects.prefetch_related('attachments', 'comentaris', 'assignacio', 'observadors')\
            .order_by('-attachments__data', '-comentaris__data')
        return get_object_or_404(queryset, id=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(Issue.get_types(self))
        context.update(get_context_navbar(self.request))
        context.update({
            'possibles_observadors': Usuari.objects.exclude(observats=self.get_object()),
            'possibles_assignats': Usuari.objects.exclude(assignats=self.get_object()),
            'ets_assignat': self.get_object().assignacio == Usuari.objects.get(user=self.request.user),
            'ets_observador': self.get_object().observadors.contains(Usuari.objects.get(user=self.request.user)),
            'logs': Log.objects.filter(issue=self.get_object()),
            # Necessari per la navbar
        })
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if 'guardar_subject' in request.POST:
                issue = self.get_object()
                subject = form.cleaned_data['subject']
                if subject != issue.subject:
                    log = Log(
                        issue=issue,
                        usuari=Usuari.objects.get(user=self.request.user),
                        tipus=Log.SUBJ,
                        valor_previ=issue.subject,
                        valor_nou=subject
                    )
                    log.save()
                    issue.subject = subject
                    issue.save()
            elif 'guardar_descripcio' in request.POST:
                issue = self.get_object()
                descripcio = form.cleaned_data['descripcio']
                if descripcio != issue.descripcio:
                    log = Log(
                        issue=issue,
                        usuari=Usuari.objects.get(user=self.request.user),
                        tipus=Log.DESCR,
                        valor_previ=issue.descripcio,
                        valor_nou=descripcio
                    )
                    log.save()
                    issue.descripcio = descripcio
                    issue.save()
            elif 'guardar_tipus' in request.POST:
                issue = self.get_object()
                tipus = form.cleaned_data['tipus']
                if tipus != issue.tipus:
                    log = Log(
                        issue=issue,
                        usuari=Usuari.objects.get(user=self.request.user),
                        tipus=Log.TIPUS,
                        valor_previ=issue.get_tipus_display()
                    )
                    issue.tipus = tipus
                    issue.save()
                    log.valor_nou = issue.get_tipus_display()
                    log.save()
            elif 'guardar_estat' in request.POST:
                issue = self.get_object()
                estat = form.cleaned_data['estat']
                if estat != issue.estat:
                    log = Log(
                        issue=issue,
                        usuari=Usuari.objects.get(user=self.request.user),
                        tipus=Log.ESTAT,
                        valor_previ=issue.get_estat_display(),
                    )
                    issue.estat = estat
                    issue.save()
                    log.valor_nou = issue.get_estat_display()
                    log.save()
            elif 'guardar_gravetat' in request.POST:
                issue = self.get_object()
                gravetat = form.cleaned_data['gravetat']
                log = Log(
                    issue=issue,
                    usuari=Usuari.objects.get(user=self.request.user),
                    tipus=Log.GRAV,
                    valor_previ=issue.get_gravetat_display(),
                )
                issue.gravetat = gravetat
                issue.save()
                log.valor_nou = issue.get_gravetat_display()
                log.save()
            elif 'guardar_prioritat' in request.POST:
                issue = self.get_object()
                prioritat = form.cleaned_data['prioritat']
                log = Log(
                    issue=issue,
                    usuari=Usuari.objects.get(user=self.request.user),
                    tipus=Log.PRIO,
                    valor_previ=issue.get_prioritat_display(),
                )
                issue.prioritat = prioritat
                issue.save()
                log.valor_nou = issue.get_prioritat_display()
                log.save()
            elif 'guardar_dataLimit' in request.POST:
                issue = self.get_object()
                dataLimit = form.cleaned_data['dataLimit']
                log = Log(
                    issue=issue,
                    usuari=Usuari.objects.get(user=self.request.user),
                    tipus=Log.LIMIT,
                    valor_previ=str(issue.dataLimit),
                    valor_nou=str(dataLimit)
                )
                log.save()
                issue.dataLimit = dataLimit
                issue.save()
            elif 'guardar_bloquejat' in request.POST:
                issue = self.get_object()
                motiuBloqueig = form.cleaned_data['motiuBloqueig']
                log = Log(
                    issue=issue,
                    usuari=Usuari.objects.get(user=self.request.user),
                    tipus=Log.BLOQ,
                    valor_previ=str(issue.bloquejat),
                )
                if motiuBloqueig is None:
                    issue.bloquejat = False
                else:
                    issue.bloquejat = True
                log.valor_nou = str(issue.bloquejat)
                log.save()
                issue.motiuBloqueig = motiuBloqueig
                issue.save()
            elif 'afegir_attachment' in request.POST:
                attachment_form = AttachmentForm(request.POST, request.FILES)
                if attachment_form.is_valid():
                    attachment = attachment_form.save(commit=False)
                    attachment.issue = self.get_object()
                    attachment.save()
                    log = Log(
                        issue=attachment.issue,
                        usuari=Usuari.objects.get(user=self.request.user),
                        tipus=Log.ADD_ATT,
                        valor_nou=attachment.document.name
                    )
                    log.save()
            elif 'afegir_comentari' in request.POST:
                comentari_form = ComentariForm(request.POST, request.FILES)
                if comentari_form.is_valid():
                    comentari = comentari_form.save(commit=False)
                    comentari.issue = self.get_object()
                    comentari.autor = Usuari.objects.get(user=self.request.user)
                    comentari.save()
            elif 'afegir_tag' in request.POST:
                tag_form = TagForm(request.POST, request.FILES)
                is_valid = tag_form.is_valid()
                tag = tag_form.cleaned_data['tag']
                issue = self.get_object()
                issue.tags.add(tag)
                log = Log(
                    issue=issue,
                    usuari=Usuari.objects.get(user=self.request.user),
                    tipus=Log.ADD_TAG,
                    valor_nou=tag.nom
                )
                log.save()
                issue.save()
            elif 'guardar_assignat' in request.POST:
                issue = self.get_object()
                id_assignat = request.POST.get('assignat')
                assignat = get_object_or_404(Usuari, pk=id_assignat)
                log = Log(
                    issue=issue,
                    usuari=Usuari.objects.get(user=self.request.user),
                    tipus=Log.ASSIGN,
                    valor_nou=assignat.user.first_name
                )
                if issue.assignacio:
                    log.valor_previ = issue.assignacio.user.first_name
                else:
                    log.valor_previ = "Sense assignar"
                log.save()
                issue.assignacio = assignat
                issue.save()
            elif 'guardar_observador' in request.POST:
                issue = self.get_object()
                id_observador = request.POST.get('observador')
                observador = get_object_or_404(Usuari, pk=id_observador)
                issue.observadors.add(observador)
                issue.save()
            elif 'autoassignar' in request.POST:
                usuari = Usuari.objects.get(user=self.request.user)
                issue = self.get_object()
                log = Log(
                    issue=issue,
                    usuari=usuari,
                    tipus=Log.ASSIGN
                )
                if issue.assignacio:
                    log.valor_previ = issue.assignacio.user.first_name
                else:
                    log.valor_previ = "Sense assignar"
                if issue.assignacio == usuari:
                    issue.assignacio = None
                    log.valor_nou = "Sense assignar"
                else:
                    issue.assignacio = usuari
                    log.valor_nou = usuari.user.first_name
                log.save()
                issue.save()
            elif 'autoobservar' in request.POST:
                usuari = Usuari.objects.get(user=self.request.user)
                issue = self.get_object()
                if issue.observadors.contains(usuari):
                    issue.observadors.remove(usuari)
                else:
                    issue.observadors.add(usuari)
                issue.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        # Sobreescivim la success url per tornar a on estàvem
        return self.request.path


class CrearBulkView(IsAuthenticatedMixin, FormView):
    model = Issue
    template_name = 'issue_bulk.html'
    form_class = IssueBulkForm
    success_url = reverse_lazy('tots_issues')

    def form_valid(self, form):
        subject_text = form.cleaned_data['subjects']
        subjects = subject_text.splitlines()
        issues = []
        for subject in subjects:
            issue = Issue(
                subject=subject,
                creador=Usuari.objects.get(user=self.request.user)
            )
            issues.append(issue)
            log = Log(
                issue=issue,
                usuari=issue.creador,
                tipus=Log.CREAR
            )
            log.save()
        Issue.objects.bulk_create(issues)
        return redirect(self.success_url)


class EsborrarIssueView(IsAuthenticatedMixin, DeleteView):
    model = Issue
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('tots_issues')
    template_name = 'issue_confirm_delete.html'
    context_object_name = 'issue'

    def post(self, request, *args, **kwargs):
        issue = self.get_object()
        logs = Log.objects.filter(issue=issue)
        for log in logs:
            log.issue = None
            log.save()
        return super().post(request, *args, **kwargs)


class EsborrarAttachmemtView(IsAuthenticatedMixin, DeleteView):
    model = Attachment
    pk_url_kwarg = 'id'
    queryset = Attachment.objects.select_related('issue')
    template_name = 'attachment_confirm_delete.html'
    context_object_name = 'attachment'

    def get_success_url(self):
        id_issue = self.object.issue.id
        return reverse('editar_issue', kwargs={'id': id_issue})

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        Log.objects.create(
            issue=self.object.issue,
            usuari=Usuari.objects.get(user=self.request.user),
            tipus=Log.DEL_ATT,
            valor_previ=self.object.document.name
        )
        return super().post(request, *args, **kwargs)


class EsborrarTagIssueView(IsAuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        id_issue = self.kwargs.get('id_issue')
        nom_tag = self.kwargs.get('nom_tag')

        issue = get_object_or_404(Issue, id=id_issue)
        tag = get_object_or_404(Tag, nom=nom_tag)

        issue.tags.remove(tag)

        Log.objects.create(
            issue=issue,
            usuari=Usuari.objects.get(user=self.request.user),
            tipus=Log.DEL_TAG,
            valor_previ=tag.nom
        )

        return redirect(request.META.get('HTTP_REFERER'))


class EsborrarAssignacioIssue(IsAuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        id_issue = self.kwargs.get('id_issue')
        issue = get_object_or_404(Issue, id=id_issue)
        Log.objects.create(
            issue=issue,
            usuari=Usuari.objects.get(user=self.request.user),
            tipus=Log.ASSIGN,
            valor_previ=issue.assignacio.user.first_name,
            valor_nou="Sense assignar"
        )
        issue.assignacio = None
        issue.save()

        return redirect(request.META.get('HTTP_REFERER'))


class EsborrarObservadorIssue(IsAuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        id_issue = self.kwargs.get('id_issue')
        id_usuari = self.kwargs.get('id_usuari')

        issue = get_object_or_404(Issue, id=id_issue)
        usuari = get_object_or_404(Usuari, pk=id_usuari)

        issue.observadors.remove(usuari)
        issue.save()

        return redirect(request.META.get('HTTP_REFERER'))
