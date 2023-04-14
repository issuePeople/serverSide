from rest_framework import viewsets
from issues.models import Issue
from . import serializers


class IssuesView(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    models = Issue
    serializer_class = serializers.IssueSerializer
    permission_classes = []
