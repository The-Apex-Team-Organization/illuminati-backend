from django.db import models
from enums.roles import Role


class User(models.Model):
    id = models.BigAutoField(primary_key = True)
    username = models.TextField(unique = True)
    email = models.TextField(unique = True)
    password = models.TextField()
    role = models.CharField(max_length = 20, default = Role.MASON)
    is_inquisitor = models.BooleanField(default = False)

    class Meta:
        db_table = 'users'
        managed = False



class InvitedUser(models.Model):
    id = models.BigAutoField(primary_key = True)
    email = models.TextField(unique = True)

    class Meta:
        db_table = 'invited_users'
        managed = False



class UserPromotion(models.Model):
    id = models.BigAutoField(primary_key = True)

    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        db_column = 'user_id',
        unique = True,
        related_name = '+'
    )

    date_of_last_promotion = models.DateField()
    is_promote_requested = models.BooleanField()



    class Meta:
        db_table = 'users_promotions'
        managed = False

