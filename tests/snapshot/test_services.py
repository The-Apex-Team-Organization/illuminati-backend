from unittest.mock import patch
from django.test import TestCase
from apps.snapshot.services import get_all_records


class GetAllRecordsTest(TestCase):
    @patch("apps.snapshot.services.Record.objects")
    def test_get_all_records_calls_all(self, mock_objects):
        mock_queryset = mock_objects.all.return_value

        result = get_all_records()

        mock_objects.all.assert_called_once()
        self.assertEqual(result, mock_queryset)