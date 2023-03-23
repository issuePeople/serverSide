from django.views.generic import FormView, TemplateView
from django.urls import reverse
from django.shortcuts import redirect, render
from . import forms, models


class CrearIssueView(FormView):
    model = models.Issue
    template_name = 'issue_form.html'
    form_class = forms.IssueForm

    def get_success_url(self):
        return reverse('tots_issues')

    def post(self, request):
        form = forms.IssueForm(request.POST)
        if form.is_valid():
            # El creador de l'Issue serà l'usuari que fa la request
            newIssue = form.save(commit=False)
            newIssue.creador = models.Usuari.objects.get(user=self.request.user)
            newIssue.save()
        return redirect(self.get_success_url())


class ListIssueView(TemplateView):
    model = models.Issue
    template_name = 'issue_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Temporalment, ordenem per data de creació
        issues = models.Issue.objects.all().order_by('-dataCreacio')
        print("hola")
        print(issues)
        context.update({'issues': issues})
        return context
