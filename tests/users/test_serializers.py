from unittest.mock import patch
from django.test import TestCase
from apps.users.serializers import UserSerializer


class UserSerializerTest(TestCase):

    def setUp(self):
        self.user_data = {
            "id": 1,
            "username": "testUser",
            "email": "testUser@example.com",
            "role": "Mason"
        }


    @patch("apps.users.serializers.User.objects.filter")
    def test_serializer_serializes_all_fields(self, mock_filter):
        mock_filter.return_value.exists.return_value = False
        serializer = UserSerializer(data = self.user_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], "testUser")
        self.assertIn('email', serializer.validated_data)


    @patch("apps.users.serializers.User.objects.filter")
    def test_serializer_dynamic_fields(self, mock_filter):
        mock_filter.return_value.exists.return_value = False
        data = {"username": "testUser"}
        serializer = UserSerializer(data = data, fields = ['username'])

        self.assertTrue(serializer.is_valid())
        self.assertEqual(set(serializer.validated_data.keys()), {"username"})
