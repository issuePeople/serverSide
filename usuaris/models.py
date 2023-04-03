from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Usuari(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    bio = models.CharField(max_length=210, null=True, blank=True, verbose_name=_('Bio'))
