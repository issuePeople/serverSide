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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issues = models.Issue.objects.all()
        print("hola")
        print(issues)
        context.update({'issues': issues})
        return context
