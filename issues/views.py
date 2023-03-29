from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from . import forms, models


class ListIssueView(TemplateView):
    model = models.Issue
    template_name = 'issue_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Temporalment, ordenem per data de creació
        issues = models.Issue.objects.all().order_by('-dataCreacio')
        context.update({'issues': issues})
        return context


class CrearIssueView(CreateView):
    model = models.Issue
    template_name = 'issue_form.html'
    form_class = forms.IssueForm
    success_url = reverse_lazy('tots_issues')

    def form_valid(self, form):
        # Especifiquem el creador de l'issue
        form.instance.creador = models.Usuari.objects.get(user=self.request.user)
        return super().form_valid(form)
