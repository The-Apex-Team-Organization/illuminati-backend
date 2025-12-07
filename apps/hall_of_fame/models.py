from django.db import models


class HallOfFame(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.TextField(unique=True)
    email = models.TextField(unique=True)

    class Meta:
        db_table = "hall_of_fame"
        managed = False
