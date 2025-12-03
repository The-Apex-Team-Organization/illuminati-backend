from django.db import models
from enums.roles import Role, VoteEnum
from apps.authentific.models import User


class Votes(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.TextField()
    is_active = models.BooleanField()
    amount_of_agreed = models.BigIntegerField()
    amount_of_disagreed = models.BigIntegerField()
    user_in_question_id = models.BigIntegerField()
    vote_type = models.TextField()


    class Meta:
        db_table = 'votes'
        managed = False


class VoteTypes(models.Model):
    id = models.BigAutoField(primary_key = True)

    vote_type = models.CharField(
        max_length = 20,
        choices = [(v.value, v.value) for v in VoteEnum],
        default = VoteEnum.PROMOTE_TO_SILVER.value,
    )

    user_role = models.CharField(
        max_length = 20,
        choices = [(role.value, role.value) for role in Role],
        default=Role.MASON.value
    )


    class Meta:
        db_table  = 'vote_types'
        managed = False


class VoteUsers(models.Model):
    id = models.BigAutoField(primary_key = True)
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    vote_id = models.ForeignKey(Votes, on_delete = models.CASCADE)
    is_voted = models.BooleanField()


    class Meta:
        db_table = 'vote_users'
        managed = False


class UsersPromotions(models.Model):
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
