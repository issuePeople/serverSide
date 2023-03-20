import django_tables2 as tables
from . import models


class IssuesTable(tables.Table):
    assignacio = tables.TemplateColumn(template_code='{{ record.assignacio.username }}')

    class Meta:
        model = models.Issue
        template_name = "django_tables2/bootstrap4.html"
        fields = ("tipus", "gravetat", "prioritat", "subject", "estat", "dataModificacio", "assignacio")
