from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Usuari(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=_('Identificador'))
    username = models.CharField(max_length=100, null=False, blank=False, unique=True, verbose_name=_('Nom d''usuari'))

