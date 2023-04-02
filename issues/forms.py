from django import forms
from issues import models


class IssueForm(forms.ModelForm):
    class Meta:
        model = models.Issue
        fields = ('subject', 'descripcio', 'tipus', 'estat', 'gravetat', 'prioritat', 'assignacio', 'dataLimit', 'bloquejat', 'motiuBloqueig')


class IssueBulkForm(forms.Form):
    subjects = forms.CharField(widget=forms.Textarea)
