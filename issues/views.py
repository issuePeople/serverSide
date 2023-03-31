from django.views.generic import TemplateView, CreateView, UpdateView
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


class EditarIssueView(UpdateView):
    model = models.Issue
    template_name = 'issue_edit.html'
    form_class = forms.IssueForm
    success_url = None

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        is_valid_form = form.is_valid()
        if 'save_subject' in request.POST:
            self.object = self.get_object()
            subject = form.cleaned_data['subject']
            self.object.subject = subject
            self.object.save()
            return self.form_valid(form)

    def get_success_url(self):
        # Sobreescivim la success url per tornar a on estàvem
        return self.request.path


class CrearBulkView(TemplateView):
    template_name = 'issue_bulk.html'
