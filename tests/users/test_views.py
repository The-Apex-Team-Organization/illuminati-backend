from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from rest_framework import status
from apps.users.views import UsersListView, UserDetailView, EmailView
from apps.users.permissions import IsGoldMason


class UsersListViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = UsersListView.as_view()


    @patch("apps.users.views.get_all_users")
    @patch.object(IsGoldMason, 'has_permission', return_value = True)
    def test_get_users_list_returns_data(self, mock_permission, mock_get_all):
        mock_user = MagicMock()
        mock_get_all.return_value = [mock_user]
        request = self.factory.get("/users/")
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["status"], "OK")


    @patch.object(IsGoldMason, 'has_permission', return_value = False)
    def test_get_users_list_forbidden(self, mock_permission):
        request = self.factory.get("/users/")
        view = UsersListView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)



class UserDetailViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = UserDetailView.as_view()


    @patch("apps.users.views.get_user_by_id")
    @patch.object(IsGoldMason, 'has_permission', return_value = True)
    def test_get_user_detail_found(self, mock_permission, mock_get_by_id):
        mock_user = MagicMock()
        mock_get_by_id.return_value = mock_user
        request = self.factory.get("/users/1/")
        response = self.view(request, user_id = 1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)


    @patch("apps.users.views.get_user_by_id")
    @patch.object(IsGoldMason, 'has_permission', return_value = True)
    def test_get_user_detail_not_found(self, mock_permission, mock_get_by_id):
        mock_get_by_id.return_value = None
        request = self.factory.get("/users/999/")
        response = self.view(request, user_id = 999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User not found")



class EmailViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = EmailView.as_view()


    @patch("apps.users.views.get_all_users")
    @patch("apps.users.views.get_all_invited_users")
    @patch("apps.users.views.get_all_emails")
    def test_get_emails_returns_sorted_list(self, mock_get_all_emails, mock_get_invited, mock_get_users):
        mock_get_invited.return_value = [MagicMock(email = "invited@gmail.com")]
        mock_get_users.return_value = [MagicMock(email = "exists@gmail.com")]
        mock_get_all_emails.return_value = ["exists@gmail.com", "invited@gmail.com"]

        request = self.factory.get("/emails/")
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("participants", response.data)
        self.assertEqual(response.data["participants"], ["exists@gmail.com", "invited@gmail.com"])


    @patch("apps.users.views.get_all_users")
    @patch("apps.users.views.get_all_invited_users")
    @patch("apps.users.views.get_all_emails")
    def test_get_emails_no_users(self, mock_get_all_emails, mock_get_invited, mock_get_users):
        mock_get_invited.return_value = []
        mock_get_users.return_value = []
        mock_get_all_emails.return_value = []

        request = self.factory.get("/emails/")
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "No users")
