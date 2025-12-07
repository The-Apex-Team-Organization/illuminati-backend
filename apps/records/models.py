from django.db import models


class Record(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    x = models.FloatField()
    y = models.FloatField()
    type = models.CharField(max_length=20)
    description = models.TextField(max_length=20)
    img_path = models.CharField(max_length=1024)
    additional_info = models.CharField(max_length=100)

    class Meta:
        db_table = "records"
        managed = False


class RecordActivityUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    record_id = models.BigIntegerField()
    like_status = models.BooleanField(default=True)

    class Meta:
        db_table = "record_activity_user"
        managed = False
        unique_together = (("user_id", "record_id"),)
