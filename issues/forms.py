from django import forms
from issues import models


class IssueForm(forms.ModelForm):
    class Meta:
        model = models.Issue
        fields = '__all__'
