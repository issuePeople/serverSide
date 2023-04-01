from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


class IsAuthenticatedMixin(LoginRequiredMixin):
    def get_login_url(self):
        return reverse('login')
