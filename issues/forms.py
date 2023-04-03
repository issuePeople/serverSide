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


class TagForm(forms.ModelForm):
    nom = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        color = cleaned_data.get('color')

        if nom and color:
            tag, created = models.Tag.objects.get_or_create(nom=nom, defaults={'color': color})
            cleaned_data['tag'] = tag
        return cleaned_data

    class Meta:
        model = models.Tag
        fields = ('nom', 'color')


class IssueForm(forms.ModelForm):
    attachment = AttachmentForm()
    comenntari = ComentariForm()
    tag = TagForm()

    class Meta:
        model = models.Issue
        fields = ('subject', 'descripcio', 'tipus', 'estat', 'gravetat', 'prioritat', 'assignacio', 'dataLimit', 'bloquejat', 'motiuBloqueig')


class IssueBulkForm(forms.Form):
    subjects = forms.CharField(widget=forms.Textarea)
