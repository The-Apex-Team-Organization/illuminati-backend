from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .services import (
    get_all_users,
    get_user_by_id,
    get_all_invited_users,
    get_all_emails,
    invite_user,
)
from .permissions import IsGoldMason, IsGoldMasonOrArchitect
import requests
import logging

logger = logging.getLogger(__name__)


class UsersListView(APIView):
    permission_classes = [IsGoldMason]

    def get(self, request):
        try:
            users = get_all_users()
            serializer = UserSerializer(users, many=True)

            return Response(
                {"status": "OK", "notification": "All users", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        except PermissionDenied:
            return Response(
                {"status": "FORBIDDEN", "notification": "Access denied"},
                status=status.HTTP_403_FORBIDDEN,
            )


class UserDetailView(APIView):
    permission_classes = [IsGoldMason]

    def get(self, request, user_id):
        user = get_user_by_id(user_id)

        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EmailView(APIView):
    def get(self, request):
        invited_emails = get_all_invited_users()
        exists_emails = get_all_users()

        if len(invited_emails) == 0 and len(exists_emails) == 0:
            return Response({"error": "No users"}, status=status.HTTP_404_NOT_FOUND)

        response = {
            "statusCode": 200,
            "participants": get_all_emails(invited_emails, exists_emails),
            "headers": [{"name": "Content-Type", "values": ["application/json"]}],
        }

        return Response(response, status=status.HTTP_200_OK)


class InviteView(APIView):
    permission_classes = [IsGoldMasonOrArchitect]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        result = invite_user(email)

        if result["status"] == "success":
            payload = {
                "topic": "Today's post: quick read",
                "text": (
                    "Hello,\n\nToday's post is available at http://localhost:5173/. "
                    "It's a short read you can open anytime. We'll deliver a single "
                    "follow-up message to all subscribers later with a small update.\n\n"
                    "Thank you for subscribing."
                ),
                "target_emails": [email],
            }

            try:
                response = requests.post(
                    "http://docker_go:8080/send_letter",
                    json=payload,
                    timeout=3,
                )
                if response.status_code != 200:
                    logger.error(f"Mailer error: {response.text}")
            except Exception as e:
                logger.exception(f"Failed to send mail via Go service: {e}")

            return Response(
                {"message": result["message"]}, status=status.HTTP_201_CREATED
            )

        elif result["status"] in ["exists", "invited"]:
            return Response(
                {"message": result["message"]}, status=status.HTTP_409_CONFLICT
            )

        return Response(
            {"error": result["message"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
