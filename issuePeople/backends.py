from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from usuaris.models import Usuari


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False


class CustomModelBackend(ModelBackend):
    # Fem override the la creació d'usuaris quan fem log in amb Google
    # per crear instància d'Usuari (a més del User de Django)
    def create_user(self, **kwargs):
        user = User(**kwargs)
        user.save(using=self._db)
        Usuari.objects.create(user=user)
        return user
