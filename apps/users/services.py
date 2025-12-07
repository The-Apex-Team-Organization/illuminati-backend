from .models import User, InvitedUser
from .serializers import InvitedUserSerializer, UserSerializer


def get_all_users():
    return User.objects.all()


def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)

    except User.DoesNotExist:
        return None


def get_all_invited_users():
    return InvitedUser.objects.all()


def get_all_emails(invited_emails, exists_emails):
    invited_users_serializer = InvitedUserSerializer(
        invited_emails, fields=["email"], many=True
    )
    exists_users_serializer = UserSerializer(exists_emails, fields=["email"], many=True)

    invited_emails = []
    exists_emails = []

    for invited_email in invited_users_serializer.data:
        invited_emails.append(invited_email["email"])

    for exists_email in exists_users_serializer.data:
        exists_emails.append(exists_email["email"])

    emails = sorted(invited_emails + exists_emails)

    return emails


def invite_user(email: str):
    if User.objects.filter(email=email).exists():
        return {"status": "exists", "message": "User with this email already exists"}

    _, created = InvitedUser.objects.get_or_create(email=email)

    if not created:
        return {"status": "invited", "message": "User already invited"}

    return {"status": "success", "message": "Invitation created successfully"}
