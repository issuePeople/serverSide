from django import forms
from issues import models


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = models.Attachment
        fields = ('document',)


class ComentariForm(forms.ModelForm):
    class Meta:
        model = models.Comentari
        fields = ('text', )


class IssueForm(forms.ModelForm):
    attachment = AttachmentForm()
    comenntari = ComentariForm()

    class Meta:
        model = models.Issue
        fields = ('subject', 'descripcio', 'tipus', 'estat', 'gravetat', 'prioritat', 'assignacio', 'dataLimit', 'bloquejat', 'motiuBloqueig')


class IssueBulkForm(forms.Form):
    subjects = forms.CharField(widget=forms.Textarea)
