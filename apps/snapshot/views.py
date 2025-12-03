from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .models import Record
from .serializers import RecordSerializer
from .services import get_all_records
import json

class RecordsBackupView(APIView):
    def get(self, request):
        records = get_all_records()

        if not records.exists():
            return Response(
                {"error": "No records found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RecordSerializer(records, many=True)
        json_data = json.dumps(serializer.data, indent=2, ensure_ascii=False)

        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="records_backup.json"'
        return response


class RecordsRestoreView(APIView):
    def post(self, request):
        
        try:
            data = request.data
            if not isinstance(data, list):
                return Response(
                    {"error": "Expected a list of records"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception:
            return Response(
                {"error": "Invalid JSON"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        serializer = RecordSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save() 
            return Response(
                {"status": "Records restored successfully", "count": len(data)},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
