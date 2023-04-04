from django.views.generic import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View
from django_filters.views import FilterView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from issuePeople.mixins import IsAuthenticatedMixin
from .models import Issue, Tag, Attachment
from .forms import IssueForm, IssueBulkForm, AttachmentForm, ComentariForm, TagForm
from usuaris.models import Usuari
from .filters import IssueFilter


class ListIssueView(IsAuthenticatedMixin, FilterView):
    model = Issue
    template_name = 'issue_list.html'
    filterset_class = IssueFilter
    context_object_name = 'issues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(Issue.get_types(self))
        context.update({
            'usuaris': Usuari.objects.all(),
            'tags': Tag.objects.all()
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

    def form_valid(self, form):
        # Especifiquem el creador de l'issue
        form.instance.creador = Usuari.objects.get(user=self.request.user)
        return super().form_valid(form)


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
        context.update({
            'possibles_observadors': Usuari.objects.exclude(observats=self.get_object()),
            'possibles_assignats': Usuari.objects.exclude(assignats=self.get_object()),
            'ets_assignat': self.get_object().assignacio == Usuari.objects.get(user=self.request.user),
            'ets_observador': self.get_object().observadors.contains(Usuari.objects.get(user=self.request.user))
        })
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if 'guardar_subject' in request.POST:
                issue = self.get_object()
                subject = form.cleaned_data['subject']
                issue.subject = subject
                issue.save()
            if 'guardar_descripcio' in request.POST:
                issue = self.get_object()
                descripcio = form.cleaned_data['descripcio']
                issue.descripcio = descripcio
                issue.save()
            if 'guardar_tipus' in request.POST:
                issue = self.get_object()
                tipus = form.cleaned_data['tipus']
                issue.tipus = tipus
                issue.save()
            if 'guardar_estat' in request.POST:
                issue = self.get_object()
                estat = form.cleaned_data['estat']
                issue.estat = estat
                issue.save()
            if 'guardar_gravetat' in request.POST:
                issue = self.get_object()
                gravetat = form.cleaned_data['gravetat']
                issue.gravetat = gravetat
                issue.save()
            if 'guardar_prioritat' in request.POST:
                issue = self.get_object()
                prioritat = form.cleaned_data['prioritat']
                issue.prioritat = prioritat
                issue.save()
            if 'afegir_attachment' in request.POST:
                attachment_form = AttachmentForm(request.POST, request.FILES)
                if attachment_form.is_valid():
                    attachment = attachment_form.save(commit=False)
                    attachment.issue = self.get_object()
                    attachment.save()
            if 'afegir_comentari' in request.POST:
                comentari_form = ComentariForm(request.POST, request.FILES)
                if comentari_form.is_valid():
                    comentari = comentari_form.save(commit=False)
                    comentari.issue = self.get_object()
                    comentari.autor = Usuari.objects.get(user=self.request.user)
                    comentari.save()
            if 'afegir_tag' in request.POST:
                tag_form = TagForm(request.POST, request.FILES)
                is_valid = tag_form.is_valid()
                tag = tag_form.cleaned_data['tag']
                issue = self.get_object()
                issue.tags.add(tag)
                issue.save()
            if 'autoassignar' in request.POST:
                usuari = Usuari.objects.get(user=self.request.user)
                issue = self.get_object()
                if issue.assignacio == usuari:
                    issue.assignacio = None
                else:
                    issue.assignacio = usuari
            if 'autoobservar' in request.POST:
                usuari = Usuari.objects.get(user=self.request.user)
                issue = self.get_object()
                if issue.observadors.contains(usuari):
                    issue.observadors.remove(usuari)
                else:
                    issue.observadors.add(usuari)
            return self.form_valid(form)
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
        Issue.objects.bulk_create(issues)
        return redirect(self.success_url)


class EsborrarIssueView(IsAuthenticatedMixin, DeleteView):
    model = Issue
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('tots_issues')
    template_name = 'issue_confirm_delete.html'
    context_object_name = 'issue'


class EsborrarAttachmemtView(IsAuthenticatedMixin, DeleteView):
    model = Attachment
    pk_url_kwarg = 'id'
    queryset = Attachment.objects.select_related('issue')
    template_name = 'attachment_confirm_delete.html'
    context_object_name = 'attachment'

    def get_success_url(self):
        id_issue = self.object.issue.id
        return reverse('editar_issue', kwargs={'id': id_issue})


class EsborrarTagIssueView(View):
    def get(self, request, *args, **kwargs):
        id_issue = self.kwargs.get('id_issue')
        nom_tag = self.kwargs.get('nom_tag')

        issue = get_object_or_404(Issue, id=id_issue)
        tag = get_object_or_404(Tag, nom=nom_tag)

        issue.tags.remove(tag)

        return redirect(request.META.get('HTTP_REFERER'))
