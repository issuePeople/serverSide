from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html
from django.utils.translation import gettext_lazy as _
from issuePeople import settings


def get_default_avatar_url():
    return settings.DEFAULT_AVATAR_URL


class Usuari(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    bio = models.CharField(max_length=210, null=True, blank=True, verbose_name=_('Bio'))
    avatar = models.FileField(default=get_default_avatar_url(), upload_to='avatar/', verbose_name=_('Avatar'))
