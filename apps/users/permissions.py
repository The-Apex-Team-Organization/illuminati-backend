import jwt
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from django.conf import settings
from .models import User
from enums.roles import Role


class IsGoldMason(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return False

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["id"])

            if user.role != Role.GOLD_MASON.value:
                raise PermissionDenied("Only GoldMasons can access this endpoint")

            return True

        except (jwt.DecodeError, jwt.ExpiredSignatureError, User.DoesNotExist):
            raise PermissionDenied("Invalid or expired token")


class IsArchitect(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return False

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["id"])

            if user.role != Role.ARCHITECT.value:
                raise PermissionDenied("Only Architects can access this endpoint")

            return True

        except (jwt.DecodeError, jwt.ExpiredSignatureError, User.DoesNotExist):
            raise PermissionDenied("Invalid or expired token")


class IsGoldMasonOrArchitect(BasePermission):
    def has_permission(self, request, view):
        return IsGoldMason().has_permission(
            request, view
        ) or IsArchitect().has_permission(request, view)
