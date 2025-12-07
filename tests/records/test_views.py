from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from io import BytesIO
from django.conf import settings
import tempfile
import jwt


class RecordListViewTest(APITestCase):
    @patch("apps.records.views.get_all_records")
    def test_get_records_success(self, mock_get_all_records):
        mock_get_all_records.return_value = [
            type(
                "Record",
                (),
                {
                    "id": 1,
                    "name": "R1",
                    "x": 1.0,
                    "y": 2.0,
                    "type": "UFO",
                    "description": "desc",
                    "img_path": "/img.png",
                    "additional_info": "info",
                },
            )()
        ]

        url = reverse("records-all")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        self.assertEqual(len(response.data["data"]), 1)


class RecordCreateViewTest(APITestCase):
    @patch("apps.records.views.create_record")
    def test_create_record_success(self, mock_create_record):
        settings.BASE_DIR = tempfile.gettempdir()

        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.name = "R1"
        mock_record.x = 1.0
        mock_record.y = 2.0
        mock_record.type = "UFO"
        mock_record.description = "desc"
        mock_record.img_path = "/images/test.png"
        mock_record.additional_info = "info"
        mock_create_record.return_value = mock_record

        img = BytesIO(b"fake image data")
        img.name = "test.png"

        url = reverse("records-create")
        data = {
            "name": "R1",
            "x": 1.0,
            "y": 2.0,
            "type": "UFO",
            "description": "desc",
            "additional_info": "info",
            "img": img,
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "OK")
        self.assertEqual(
            response.data["notification"], "Record created successfully")
        mock_create_record.assert_called_once()

    def test_create_record_missing_image(self):
        settings.BASE_DIR = tempfile.gettempdir()

        url = reverse("records-create")
        data = {
            "name": "R1",
            "x": 1.0,
            "y": 2.0,
            "type": "UFO",
            "description": "desc",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Image is required", str(response.data))

    def test_create_record_invalid_data(self):
        settings.BASE_DIR = tempfile.gettempdir()

        url = reverse("records-create")
        data = {"name": ""}

        response = self.client.post(url, data)

        self.assertEqual(response.data["status"], "ERROR")
        self.assertIn("Invalid data", response.data["notification"])


class RecordDetailViewTest(APITestCase):
    @patch("apps.records.views.get_record_by_id")
    def test_get_record_success(self, mock_get_record_by_id):
        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.name = "R1"
        mock_record.x = 1.0
        mock_record.y = 2.0
        mock_record.type = "UFO"
        mock_record.description = "desc"
        mock_record.img_path = "/images/test.png"
        mock_record.additional_info = "info"

        mock_get_record_by_id.return_value = mock_record

        url = reverse("records-detail", args=[1])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        self.assertEqual(response.data["notification"], "Record details")
        mock_get_record_by_id.assert_called_once_with(1, user_id=None)

    @patch("apps.records.views.get_record_by_id")
    def test_get_record_not_found(self, mock_get_record_by_id):
        mock_get_record_by_id.return_value = None

        url = reverse("records-detail", args=[99])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["status"], "ERROR")
        self.assertIn("Record not found", response.data["notification"])
        mock_get_record_by_id.assert_called_once_with(99, user_id=None)


class RecordEraseViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("records-erase")
        self.token = jwt.encode(
            {"role": "GoldMason"}, settings.SECRET_KEY, algorithm="HS256"
        )

    @patch("apps.records.views.erase_all_records")
    def test_erase_records_success(self, mock_erase_all):
        response = self.client.post(
            self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        self.assertIn("All records erased", response.data["notification"])
        mock_erase_all.assert_called_once()

    def test_erase_records_missing_token(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Missing or invalid token",
                      response.data["notification"])

    def test_erase_records_invalid_token(self):
        response = self.client.post(
            self.url, HTTP_AUTHORIZATION="Bearer invalidtoken")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid token", response.data["notification"])

    def test_erase_records_expired_token(self):
        expired_token = jwt.encode(
            {"role": "GoldMason", "exp": 0},
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        response = self.client.post(
            self.url, HTTP_AUTHORIZATION=f"Bearer {expired_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Token expired", response.data["notification"])

    def test_erase_records_forbidden_role(self):
        token = jwt.encode(
            {"role": "WithoutRole"}, settings.SECRET_KEY, algorithm="HS256"
        )
        response = self.client.post(
            self.url, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("unauthorized", response.data["notification"].lower())


class LikeRecordViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("records-like", args=[1])
        self.token = jwt.encode(
            {"id": 1}, settings.SECRET_KEY, algorithm="HS256")

    @patch("apps.records.views.get_record_by_id")
    @patch("apps.records.views.like_record")
    def test_like_record_success(self, mock_like_record, mock_get_record_by_id):
        mock_get_record_by_id.return_value = True
        mock_like_record.return_value = {
            "likes_count": 5, "liked_by_user": True}

        response = self.client.post(
            self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        self.assertIn("Record liked", response.data["notification"])

    def test_like_record_missing_token(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_record_invalid_token(self):
        response = self.client.post(
            self.url, HTTP_AUTHORIZATION="Bearer badtoken")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UnlikeRecordViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("records-unlike", args=[1])
        self.token = jwt.encode(
            {"id": 1}, settings.SECRET_KEY, algorithm="HS256")

    @patch("apps.records.views.get_record_by_id")
    @patch("apps.records.views.unlike_record")
    def test_unlike_record_success(self, mock_unlike_record, mock_get_record_by_id):
        mock_get_record_by_id.return_value = True
        mock_unlike_record.return_value = {
            "likes_count": 3, "liked_by_user": False}

        response = self.client.post(
            self.url, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        self.assertIn("Record unliked", response.data["notification"])

    def test_unlike_record_missing_token(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unlike_record_invalid_token(self):
        response = self.client.post(
            self.url, HTTP_AUTHORIZATION="Bearer invalid")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
