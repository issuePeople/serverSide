from storages.backends.s3boto3 import S3Boto3Storage
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from usuaris.models import Usuari


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    # Fem override the la creació d'usuaris quan fem log in amb Google
    # per crear instància d'Usuari (a més del User de Django)
    def save_user(self, request, sociallogin, form=None):
        # Agafem el mail amb què s'ha fet login
        email = sociallogin.account.extra_data['email']

        # Mirem si trobem user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            # Si existia, actualitzem valors
            user.first_name = sociallogin.account.extra_data.get('first_name', '')
            user.save()
        else:
            # Si no, creem usuari de django i nostre
            user = User(
                username=email,
                email=email,
                first_name=sociallogin.account.extra_data.get('first_name', '')
            )
            user.set_unusable_password()
            user.save()

            usuari = Usuari(
                user=user
            )
            usuari.save()

            # Enllacem la social account al user
            sociallogin.account.user = user
            sociallogin.account.save()

        return user
