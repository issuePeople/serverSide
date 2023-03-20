from django.views.generic import FormView
from django.urls import reverse
from django_tables2 import SingleTableView
from . import forms, models, tables


class CrearIssueView(FormView):
    model = models.Issue
    template_name = 'issue_form.html'
    form_class = forms.IssueForm

    def get_success_url(self):
        return reverse('tots_issues')


class ListIssueView(SingleTableView):
    model = models.Issue
    template_name = 'issue_list.html'
    table_class = tables.IssuesTable

    def get_queryset(self):
        queryset = super().get_queryset().select_related('assignacio')
        return queryset
