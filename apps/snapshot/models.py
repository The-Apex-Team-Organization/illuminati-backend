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