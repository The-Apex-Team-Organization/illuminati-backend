from django.test import TestCase
from apps.records.serializers import RecordSerializer
from apps.records.models import Record


class RecordSerializerTest(TestCase):
    def setUp(self):
        self.record = Record(
            id=1,
            name="Test record",
            x=1.1,
            y=2.2,
            type="UFO",
            description="desc",
            img_path="/path/img.png",
            additional_info="info",
        )

    def test_serializer_serializes_all_fields(self):
        serializer = RecordSerializer(self.record)
        data = serializer.data
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Test record")
        self.assertIn("additional_info", data)

    def test_serializer_dynamic_fields(self):
        serializer = RecordSerializer(self.record, fields=["id", "name"])
        data = serializer.data
        self.assertEqual(set(data.keys()), {"id", "name"})
