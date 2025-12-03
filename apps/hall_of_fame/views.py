from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HallOfFameSerializer
from .services import get_all_architects, send_message_to_architect


class HallOfFameListView(APIView):
    def get(self, request):
        architects = get_all_architects()
        serializer = HallOfFameSerializer(architects, many=True)
        return Response(
            {"status": "OK", "notification": "All architects", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class HallOfFameMessageView(APIView):
    def post(self, request):
        architect_id = request.data.get("architect_id")
        message = request.data.get("message")

        if not architect_id or not message:
            return Response(
                {"error": "architect_id and message are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sent = send_message_to_architect(architect_id, message)
        if not sent:
            return Response(
                {"error": "Architect not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"status": "OK", "notification": "Message sent successfully"},
            status=status.HTTP_200_OK,
        )
