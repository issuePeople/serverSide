import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Issue


class IssueFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label=_('Search'))
    tipus = django_filters.CharFilter(method='in_filter', label=_('Tipus'))
    gravetat = django_filters.CharFilter(method='in_filter', label=_('Gravetat'))
    prioritat = django_filters.CharFilter(method='in_filter', label=_('Prioritat'))
    estat = django_filters.CharFilter(method='in_filter', label=_('Estat'))
    assignacio = django_filters.CharFilter(method='in_filter', label=_('Assignació'))
    tags = django_filters.CharFilter(method='in_filter', label=_('Creador'))
    creador = django_filters.CharFilter(method='in_filter', label=_('Creador'))

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(subject__icontains=value) |
            Q(descripcio__icontains=value)
        )

    def in_filter(self, queryset, name, value):
        # Rebem les choices
        choices = value.split(',')
        # Filtrem per __in el queryset
        return queryset.filter(**{f'{name}__in': choices})

    class Meta:
        model = Issue
        fields = '__all__'
