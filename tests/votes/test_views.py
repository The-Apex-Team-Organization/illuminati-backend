from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from apps.votes.views import VotesTableView, SendVoteView, PromotionPermissionView, BanPermissionView, \
    UserPromoteView, UserBanView, CloseActiveExpiredVotesView, InquisitorManagementView
from rest_framework import status


class VoteTableViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1
        self.user.role = "Mason"


    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.services.VoteService.get_all_votes")
    @patch("apps.votes.services.VoteService.get_vote_role_raw", return_value = ["PROMOTE"])
    def test_get_votes_table(self, mock_role, mock_service, _):
        mock_service.return_value = [
            {"id": 1, "name": "Vote1", "percent": 100}
        ]

        request = self.factory.get("/votes/")
        request.user = self.user
        view = VotesTableView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        mock_service.assert_called_once()



class SendVoteViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1


    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.services.SendVoteService.commit_choice")
    @patch("apps.votes.services.SendVoteService.user_already_voted", return_value = True)
    def test_send_vote_already_voted(self, mock_already, mock_commit, _):
        request = self.factory.post(
            "/votes/sendVote/",
            {"id": 1, "choice": "AGREE"},
            content_type = "application/json"
        )
        request.user = self.user
        view = SendVoteView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "ALREADY_VOTED")

        mock_already.assert_called_once()
        mock_commit.assert_not_called()


    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.services.SendVoteService.commit_choice", return_value = True)
    @patch("apps.votes.services.SendVoteService.user_already_voted", return_value = False)
    def test_send_success_vote(self, mock_already, mock_commit, _):
        request = self.factory.post(
            "/votes/sendVote/",
            {"id": 1, "choice": "AGREE"},
            content_type = "application/json"
        )
        request.user = self.user
        view = SendVoteView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        mock_already.assert_called_once()
        mock_commit.assert_called_once()


    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.services.SendVoteService.commit_choice", return_value = False)
    @patch("apps.votes.services.SendVoteService.user_already_voted", return_value = False)
    def test_invalid_vote_request(self, mock_already, mock_commit, _):
        request = self.factory.post(
            "/votes/sendVote/",
            {"id": 1, "choice": "AGREE"},
            content_type = "application/json"
        )
        request.user = self.user
        view = SendVoteView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["status"], "CONFLICT")

        mock_already.assert_called_once()
        mock_commit.assert_called_once()



class PromotionPermissionViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1
        self.user.role = "Mason"


    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.views.PermissionService.has_promote_permission", return_value = True)
    def test_user_has_permission(self, mock_service, _):
        request = self.factory.get("/votes/promote/")
        request.user = self.user

        response = PromotionPermissionView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        mock_service.assert_called_once()



    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.views.PermissionService.has_promote_permission", return_value = False)
    def test_user_has_not_permission(self, mock_service, _):
        request = self.factory.get("/votes/promote/")
        request.user = self.user

        response = PromotionPermissionView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["status"], "REFUSED")

        mock_service.assert_called_once()



class BanPermissionViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1
        self.user.role = "Mason"


    @patch("apps.votes.views.PermissionService")
    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    def test_user_has_ban_permission(self, mock_has_perm, mock_service):
        mock_instance = mock_service.return_value
        mock_instance.has_ban_permission.return_value = True
        mock_instance.get_all_users_for_ban.return_value = [
            {"user_id": 2, "username": "user2"}
        ]

        request = self.factory.get("/votes/banPermission/")
        request.user = self.user

        response = BanPermissionView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        mock_instance.has_ban_permission.assert_called_once()
        mock_instance.get_all_users_for_ban.assert_called_once()


    @patch("apps.votes.views.PermissionService")
    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    def test_user_has_not_ban_permission(self, mock_has_perm, mock_service):
        mock_instance = mock_service.return_value
        mock_instance.has_ban_permission.return_value = False

        request = self.factory.get("/votes/banPermission/")
        request.user = self.user

        response = BanPermissionView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["status"], "REFUSED")
        mock_instance.has_ban_permission.assert_called_once()



class UserPromoteViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1
        self.user.role = "Mason"


    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.services.UserPromoteService.create_vote", return_value = True)
    def test_create_vote_for_promotion(self, mock_service, _):
        request = self.factory.patch("/votes/promote/")
        request.user = self.user

        response = UserPromoteView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        mock_service.assert_called_once()


    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.services.UserPromoteService.create_vote", return_value = False)
    def test_user_already_create_vote_for_promotion(self, mock_service, _):
        request = self.factory.patch("/votes/promote/")
        request.user = self.user

        response = UserPromoteView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "BAD_REQUEST")

        mock_service.assert_called_once()



class UserBanViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1
        self.user.name = 'test1'
        self.user.role = "Mason"


    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.services.UserBanService.create_vote", return_value = True)
    def test_create_vote_for_ban(self, mock_service, _):
        request = self.factory.patch(
            "/votes/ban/",
            {"user_id": 1, "username": "test1"},
            content_type = "application/json"
        )
        request.user = self.user

        response = UserBanView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        mock_service.assert_called_once()



    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    @patch("apps.votes.services.UserBanService.create_vote", return_value = False)
    def test_user_already_create_vote_for_ban(self, mock_service, _):
        request = self.factory.patch(
            "/votes/ban/",
            {"user_id": 1, "username": "test1"},
            content_type = "application/json"
        )
        request.user = self.user

        response = UserBanView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "BAD_REQUEST")

        mock_service.assert_called_once()



class CloseActiveExpiredVotesViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1
        self.user.role = "Mason"


    @patch("apps.votes.services.VoteService.close_votes", return_value = True)
    def test_close_votes(self, mock_service):
        request = self.factory.patch(
            "/votes/vote_close/",
            {"date_of_end": "2025-10-31 19:05:20"},
            content_type = "application/json"
        )
        request.user = self.user

        response = CloseActiveExpiredVotesView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        mock_service.assert_called_once()


    @patch("apps.votes.services.VoteService.close_votes", return_value = False)
    def test_failed_close_votes(self, mock_service):
        request = self.factory.patch(
            "/votes/vote_close/",
            {"date_of_end": "2025-10-31 19:05:20"},
            content_type = "application/json"
        )
        request.user = self.user

        response = CloseActiveExpiredVotesView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "BAD_REQUEST")

        mock_service.assert_called_once()



class InquisitorManagementViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1
        self.user.role = "Mason"


    @patch("apps.votes.views.InquisitorManagementService")
    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    def test_appoint_inquisitor_role_success(self, mock_has_perm, mock_service):
        mock_instance = mock_service.return_value
        mock_instance.appoint_inquisitor_role.return_value = True

        request = self.factory.patch("/manage_inquisitor/")
        request.user = self.user

        response = InquisitorManagementView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        self.assertEqual(response.data["notification"], "The inquisitorial role was established")

        mock_instance.appoint_inquisitor_role.assert_called_once()


    @patch("apps.votes.views.InquisitorManagementService")
    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    def test_appoint_inquisitor_role_fail(self, mock_has_perm, mock_service):
        mock_instance = mock_service.return_value
        mock_instance.appoint_inquisitor_role.return_value = False

        request = self.factory.patch("/manage_inquisitor/")
        request.user = self.user

        response = InquisitorManagementView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "BAD_REQUEST")
        self.assertEqual(response.data["notification"], "Error to appoint inquisitor role")

        mock_instance.appoint_inquisitor_role.assert_called_once()


    @patch("apps.votes.views.InquisitorManagementService")
    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    def test_remove_inquisitor_role_success(self, mock_has_perm, mock_service):
        mock_instance = mock_service.return_value
        mock_instance.remove_inquisitor_role.return_value = True

        request = self.factory.delete("/manage_inquisitor/")
        request.user = self.user

        response = InquisitorManagementView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        self.assertEqual(response.data["notification"], "The inquisitorial role was blocked")

        mock_instance.remove_inquisitor_role.assert_called_once()


    @patch("apps.votes.views.InquisitorManagementService")
    @patch("apps.votes.views.HasValidToken.has_permission", return_value = True)
    def test_remove_inquisitor_role_fail(self, mock_has_perm, mock_service):
        mock_instance = mock_service.return_value
        mock_instance.remove_inquisitor_role.return_value = False

        request = self.factory.delete("/manage_inquisitor/")
        request.user = self.user

        response = InquisitorManagementView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "BAD_REQUEST")
        self.assertEqual(response.data["notification"], "Error to block inquisitor role")

        mock_instance.remove_inquisitor_role.assert_called_once()