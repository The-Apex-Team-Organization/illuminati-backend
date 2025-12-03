from unittest.mock import patch, Mock
from django.test import TestCase
from apps.records.services import (
    get_all_records,
    erase_all_records,
    get_record_by_id,
    create_record,
)


class GetAllRecordsTest(TestCase):
    @patch("apps.records.services.RecordActivityUser.objects")
    @patch("apps.records.services.Record.objects")
    def test_get_all_records_calls_all(
        self, mock_record_objects, mock_activity_user_objects
    ):
        record1 = Mock()
        record1.id = 1
        record2 = Mock()
        record2.id = 2
        mock_record_objects.all.return_value = [record1, record2]
        mock_activity_user_objects.filter.return_value.values.return_value.annotate.return_value = [
            {"record_id": 1, "count": 5},
            {"record_id": 2, "count": 7},
        ]

        result = get_all_records()

        mock_record_objects.all.assert_called_once()
        mock_activity_user_objects.filter.assert_called_once_with(like_status=True)
        self.assertEqual(record1.likes_count, 5)
        self.assertEqual(record2.likes_count, 7)
        self.assertEqual(result, [record1, record2])


class CreateRecordTest(TestCase):
    @patch("apps.records.services.Record.objects.create")
    def test_create_record_calls_create_with_data(self, mock_create):
        data = {
            "name": "New record",
            "x": 3.0,
            "y": 4.0,
            "type": "UFO",
            "description": "desc",
            "img_path": "/img.png",
            "additional_info": "info",
        }

        mock_record = mock_create.return_value

        result = create_record(data)

        mock_create.assert_called_once_with(**data)
        self.assertEqual(result, mock_record)


class GetRecordByIdTest(TestCase):
    @patch("apps.records.services.RecordActivityUser.objects")
    @patch("apps.records.services.Record.objects")
    def test_get_record_by_id_calls_get_with_correct_id(
        self, mock_record_objects, mock_activity_user_objects
    ):
        mock_record = mock_record_objects.get.return_value
        mock_activity_user_objects.filter.return_value.count.return_value = 3

        result = get_record_by_id(5)

        mock_record_objects.get.assert_called_once_with(id=5)
        mock_activity_user_objects.filter.assert_called_once_with(
            record_id=5, like_status=True
        )
        self.assertEqual(result, mock_record)

    @patch("apps.records.services.RecordActivityUser.objects")
    @patch("apps.records.services.Record.objects")
    def test_erase_all_records_deletes_all(
        self, mock_record_objects, mock_activity_user_objects
    ):
        erase_all_records()

        mock_record_objects.all.assert_called_once()
        mock_record_objects.all.return_value.delete.assert_called_once()

        mock_activity_user_objects.all.assert_called_once()
        mock_activity_user_objects.all.return_value.delete.assert_called_once()


class LikeRecordTest(TestCase):
    @patch("apps.records.services.RecordActivityUser.objects")
    @patch("apps.records.services.Record.objects")
    def test_like_record_creates_or_updates_like(
        self, mock_record_objects, mock_activity_user_objects
    ):
        mock_record_objects.get.return_value = Mock()
        mock_activity_user_objects.filter.return_value.count.return_value = 5

        from apps.records.services import like_record

        result = like_record(user_id=10, record_id=3)

        mock_record_objects.get.assert_called_once_with(id=3)
        mock_activity_user_objects.update_or_create.assert_called_once_with(
            user_id=10,
            record_id=3,
            defaults={"like_status": True},
        )
        self.assertEqual(result, {"likes_count": 5, "liked_by_user": True})


class UnlikeRecordTest(TestCase):
    @patch("apps.records.services.RecordActivityUser.objects")
    def test_unlike_record_deletes_and_returns_updated_count(
        self, mock_activity_user_objects
    ):
        mock_activity_user_objects.filter.return_value.count.return_value = 2

        from apps.records.services import unlike_record

        result = unlike_record(user_id=1, record_id=5)

        mock_activity_user_objects.filter.assert_any_call(user_id=1, record_id=5)
        mock_activity_user_objects.filter.return_value.delete.assert_called_once()
        self.assertEqual(result, {"likes_count": 2, "liked_by_user": False})
