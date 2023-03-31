from django.views.generic import TemplateView, CreateView, UpdateView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from . import forms, models
from .filters import IssueFilter


class ListIssueView(FilterView):
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
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrem fent servir l'IssueFilter (fitlers.py)
        filter = IssueFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs.order_by(order_by)

        return queryset



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
