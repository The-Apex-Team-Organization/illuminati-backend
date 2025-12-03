from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import save_new_entry_password


class EntryView(APIView):

    def post(self, request):

        save_new_entry_password()

        return Response(
            {"status": "OK", "notification": "Entry verified"},
            status = status.HTTP_200_OK
        )

