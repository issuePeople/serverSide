import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Issue


class IssueFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label=_('Search'))

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(subject__icontains=value) |
            Q(descripcio__icontains=value)
        )

    class Meta:
        model = Issue
        fields = '__all__'
