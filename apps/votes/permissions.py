import jwt
from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from apps.users.models import User


class HasValidToken(BasePermission):

    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return False

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user = User.objects.get(id = payload["id"])
            return True

        except Exception:
            raise PermissionDenied("Invalid or expired token")
