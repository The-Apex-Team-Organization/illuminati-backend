from unittest import TestCase
from unittest.mock import patch, PropertyMock
from apps.votes.serializers import VotesSerializer, SendVotesSerializer, CloseVotesSerializer, UserBanSerializer


class TestVotesSerializerMock(TestCase):

    @patch.object(VotesSerializer, 'is_valid', return_value = True)
    @patch.object(VotesSerializer, 'validated_data', new_callable = PropertyMock)
    def test_votes_serializer_mock(self, mock_validated_data, mock_is_valid):
        mock_validated_data.return_value = {"id": 1, "name": "vote", "percent": 50.0}
        serializer = VotesSerializer(data = {})
        serializer.is_valid()

        self.assertEqual(serializer.validated_data["id"], 1)
        self.assertTrue(serializer.is_valid.called)



class TestSendVotesSerializerMock(TestCase):

    @patch.object(SendVotesSerializer, 'is_valid', return_value = True)
    @patch.object(SendVotesSerializer, 'validated_data', new_callable = PropertyMock)
    def test_send_votes_serializer_mock(self, mock_validated_data, mock_is_valid):
        mock_validated_data.return_value = {"id": 1, "choice": "yes"}
        serializer = SendVotesSerializer(data = {})
        serializer.is_valid()

        self.assertEqual(serializer.validated_data["choice"], "yes")
        self.assertTrue(serializer.is_valid.called)



class TestCloseVotesSerializerMock(TestCase):

    @patch.object(CloseVotesSerializer, 'is_valid', return_value = True)
    @patch.object(CloseVotesSerializer, 'validated_data', new_callable = PropertyMock)
    def test_close_votes_serializer_mock(self, mock_validated_data, mock_is_valid):
        mock_validated_data.return_value = {"date_of_end": "2025-11-02T12:30:00"}
        serializer = CloseVotesSerializer(data = {})
        serializer.is_valid()

        self.assertEqual(serializer.validated_data["date_of_end"], "2025-11-02T12:30:00")
        self.assertTrue(serializer.is_valid.called)



class TestUserBanSerializerMock(TestCase):

    @patch.object(UserBanSerializer, 'is_valid', return_value = True)
    @patch.object(UserBanSerializer, 'validated_data', new_callable = PropertyMock)
    def test_user_ban_serializer_mock(self, mock_validated_data, mock_is_valid):
        mock_validated_data.return_value = {"user_id": 10, "username": "mock_user"}
        serializer = UserBanSerializer(data = {})
        serializer.is_valid()

        self.assertEqual(serializer.validated_data["user_id"], 10)
        self.assertEqual(serializer.validated_data["username"], "mock_user")
        self.assertTrue(serializer.is_valid.called)
