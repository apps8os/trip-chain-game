from django.db import models

from djangotoolbox.fields import DictField


class Trip(models.Model):
    client_id = models.CharField(max_length=36)  # uuid.uuid4() is 36 chars long
    started_at = models.DateTimeField()
    trip = DictField()
