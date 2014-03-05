from django.db import models

from djangotoolbox.fields import DictField


class Trip(models.Model):
    user_id = models.CharField()
    started_at = models.DateTimeField()
    trip = DictField()
