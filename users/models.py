from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class CustomUser(AbstractUser):
    biography = models.CharField(verbose_name=_('biography'), max_length=500, blank=True)

    def get_absolute_url(self):
        if self.is_active:
            # return reverse("users:user-detail", kwargs={"pk": self.pk})
            return reverse("users:user-detail", kwargs={"username": self.username})
        return reverse("users:user-deleted-profile")