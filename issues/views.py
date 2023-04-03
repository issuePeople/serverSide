from django.views.generic import FormView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from issuePeople.mixins import IsAuthenticatedMixin
from .models import Issue, Tag
from .forms import IssueForm, IssueBulkForm, AttachmentForm, ComentariForm
from usuaris.models import Usuari
from .filters import IssueFilter


class ListIssueView(IsAuthenticatedMixin, FilterView):
    model = Issue
    template_name = 'issue_list.html'
    filterset_class = IssueFilter
    context_object_name = 'issues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'TTipus': Issue.TTIPUS,
            'TEstats': Issue.TESTATS,
            'TGravetat': Issue.TGRAVETAT,
            'TPrioritat': Issue.TPRIORITAT,
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
        pk = self.kwargs.get('pk')
        queryset = Issue.objects.prefetch_related('attachments', 'comentaris').order_by('-attachments__data', '-comentaris__data')
        return get_object_or_404(queryset, pk=pk)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if 'guardar_subject' in request.POST:
                self.object = self.get_object()
                subject = form.cleaned_data['subject']
                self.object.subject = subject
                self.object.save()
                return self.form_valid(form)
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
