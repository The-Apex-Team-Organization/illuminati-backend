from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .services import register_user, authenticate_user, get_entry_pass
from core.settings import base
from .passwords import check_password


class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data = request.data)

        if not serializer.is_valid():

            if "username" in serializer.errors or "email" in serializer.errors:
                return Response(
                    {"status": "ALREADY_EXISTS", "notification": "Credentials exist"},
                    status = status.HTTP_400_BAD_REQUEST
                )

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        try:
            user, token = register_user(**serializer.validated_data)
            return Response(
                {"status": "OK", "token": token, "notification": "Registration successful"},
                status = status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response(
                {"status": "UNAUTHORIZED", "notification": str(e)},
                status = status.HTTP_403_FORBIDDEN
            )



class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        user, token = authenticate_user(
            serializer.validated_data["email"],
            serializer.validated_data["password"]
        )

        if user:
            return Response(
                {"status": "OK", "token": token, "notification": "Login verified"},
                status = status.HTTP_200_OK
            )

        return Response(
            {"status": "UNAUTHORIZED", "notification": "Invalid credentials"},
            status = status.HTTP_400_BAD_REQUEST
        )



class EntryView(APIView):

    def post(self, request):
        secret_password = request.data.get("password")

        if not secret_password:
            return Response(
                {"status": "ERROR", "notification": "Missing password"},
                status = status.HTTP_400_BAD_REQUEST
            )

        secret_entry_password = get_entry_pass()

        if check_password(secret_password, secret_entry_password):
            return Response(
                {"status": "OK", "notification": "Entry verified"},
                status = status.HTTP_200_OK
            )

        return Response(
            {"status": "UNAUTHORIZED", "notification": "Invalid password"},
            status = status.HTTP_401_UNAUTHORIZED
        )