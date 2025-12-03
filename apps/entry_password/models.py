from django.db import models


class EntryPassword(models.Model):
    id = models.BigAutoField(primary_key = True)
    entry_password = models.TextField(unique = True)
    last_updated = models.TimeField()

    class Meta:
        db_table = 'entry_password'
        managed = False