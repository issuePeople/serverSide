from django.views.generic import FormView, TemplateView
from django.urls import reverse
from . import forms, models


class CrearIssueView(FormView):
    model = models.Issue
    template_name = 'issue_form.html'
    form_class = forms.IssueForm

    def get_success_url(self):
        return reverse('tots_issues')


class ListIssueView(TemplateView):
    model = models.Issue
    template_name = 'issue_list.html'
