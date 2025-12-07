from .models import User, InvitedUser, UserPromotion
from .passwords import hash_password, check_password
import jwt
from django.conf import settings
from datetime import timedelta, datetime
from enums.roles import Role
from django.utils import timezone
from apps.entry_password.models import EntryPassword


def generate_jwt(user, lifetime_minutes=60):
    payload = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "inquisitor" : user.is_inquisitor,
        "exp": timezone.now() + timedelta(minutes = lifetime_minutes),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = "HS256")
    return token


def register_user(username, email, password):
    invited_record = InvitedUser.objects.filter(email = email).first()

    if not invited_record:
        raise ValueError("Email is not invited")

    hashed_password = hash_password(password)

    user = User.objects.create(
        username = username, email = email, password = hashed_password, role = Role.MASON.value
    )

    UserPromotion.objects.create(
        user = user,
        date_of_last_promotion = datetime.today(),
        is_promote_requested = False,
    )

    invited_record.delete()

    token = generate_jwt(user)
    return user, token


def authenticate_user(email, password):
    try:
        user = User.objects.get(email = email)

        if check_password(password, user.password):
            token = generate_jwt(user)
            return user, token

        return None, None

    except User.DoesNotExist:
        return None, None

def get_entry_pass():
    entry_password = EntryPassword.objects.filter().first()
    return entry_password.entry_password