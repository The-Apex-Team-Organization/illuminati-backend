from unittest.mock import patch, MagicMock
from django.test import TestCase
from apps.users.services import get_all_users, get_all_invited_users, get_user_by_id, get_all_emails
from apps.users.models import User


class GetAllUsersTest(TestCase):

    @patch("apps.users.services.User.objects")
    def test_get_all_users_calls_all(self, mock_objects):
        mock_queryset = mock_objects.all.return_value

        result = get_all_users()

        mock_objects.all.assert_called_once()
        self.assertEqual(result, mock_queryset)


    @patch("apps.users.services.InvitedUser.objects")
    def test_get_all_invited_users_calls_all(self, mock_objects):
        mock_queryset = mock_objects.all.return_value

        result = get_all_invited_users()

        mock_objects.all.assert_called_once()
        self.assertEqual(result, mock_queryset)



class GetUserByIdTest(TestCase):

    @patch("apps.users.services.User.objects")
    def test_get_user_by_id_found(self, mock_objects):
        mock_user = MagicMock()
        mock_objects.get.return_value = mock_user

        result = get_user_by_id(1)

        mock_objects.get.assert_called_once_with(id = 1)
        self.assertEqual(result, mock_user)


    @patch("apps.users.services.User.objects")
    def test_get_user_by_id_not_found(self, mock_objects):
        mock_objects.get.side_effect = User.DoesNotExist

        result = get_user_by_id(999)

        mock_objects.get.assert_called_once_with(id = 999)
        self.assertIsNone(result)



class GetAllEmailsTest(TestCase):

    @patch("apps.users.services.UserSerializer")
    @patch("apps.users.services.InvitedUserSerializer")
    def test_get_all_emails_returns_sorted_emails(self, mock_invited_serializer, mock_user_serializer):
        invited_emails = [MagicMock(email = "invited@gmail.com")]
        exists_emails = [MagicMock(email = "exists@gmail.com")]

        mock_invited_serializer.return_value.data = [
            {"email": "invited@gmail.com"}
        ]
        mock_user_serializer.return_value.data = [
            {"email": "exists@gmail.com"}
        ]
        emails = get_all_emails(invited_emails, exists_emails)

        self.assertEqual(emails, ["exists@gmail.com", "invited@gmail.com"])
