from django.views.generic import FormView, CreateView, UpdateView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from issuePeople.mixins import IsAuthenticatedMixin
from . import forms, models
from usuaris.models import Usuari
from .models import Tag
from .filters import IssueFilter


class ListIssueView(IsAuthenticatedMixin, FilterView):
    model = models.Issue
    template_name = 'issue_list.html'
    filterset_class = IssueFilter
    context_object_name = 'issues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'TTipus': models.Issue.TTIPUS})
        context.update({'TEstats': models.Issue.TESTATS})
        context.update({'TGravetat': models.Issue.TGRAVETAT})
        context.update({'TPrioritat': models.Issue.TPRIORITAT})
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
    model = models.Issue
    template_name = 'issue_form.html'
    form_class = forms.IssueForm
    success_url = reverse_lazy('tots_issues')

    def form_valid(self, form):
        # Especifiquem el creador de l'issue
        form.instance.creador = models.Usuari.objects.get(user=self.request.user)
        return super().form_valid(form)


class EditarIssueView(IsAuthenticatedMixin, UpdateView):
    model = models.Issue
    template_name = 'issue_edit.html'
    form_class = forms.IssueForm
    success_url = None
    context_object_name = 'issue'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        queryset = models.Issue.objects.prefetch_related('attachments').order_by('-attachments__data')
        return get_object_or_404(queryset, pk=pk)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if 'save_subject' in request.POST:
                self.object = self.get_object()
                subject = form.cleaned_data['subject']
                self.object.subject = subject
                self.object.save()
                return self.form_valid(form)
            if 'add_attachment' in request.POST:
                attachment_form = forms.AttachmentForm(request.POST, request.FILES)
                if attachment_form.is_valid():
                    attachment = attachment_form.save(commit=False)
                    attachment.issue = self.get_object()
                    attachment.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        # Sobreescivim la success url per tornar a on estàvem
        return self.request.path


class CrearBulkView(IsAuthenticatedMixin, FormView):
    model = models.Issue
    template_name = 'issue_bulk.html'
    form_class = forms.IssueBulkForm
    success_url = reverse_lazy('tots_issues')

    def form_valid(self, form):
        subject_text = form.cleaned_data['subjects']
        subjects = subject_text.splitlines()
        issues = []
        for subject in subjects:
            issue = models.Issue(
                subject=subject,
                creador=models.Usuari.objects.get(user=self.request.user)
            )
            issues.append(issue)
        models.Issue.objects.bulk_create(issues)
        return redirect(self.success_url)
