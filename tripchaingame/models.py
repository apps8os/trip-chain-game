from django.db import models

from djangotoolbox.fields import DictField


class Trip(models.Model):
    user_id = models.CharField()
    started_at = models.DateTimeField()
    trip = DictField()
    client_version = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
