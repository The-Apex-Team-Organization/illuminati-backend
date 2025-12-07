from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .permissions import HasValidToken
from .services import VoteService,SendVoteService, PermissionService, UserPromoteService, UserBanService, \
InquisitorManagementService, UserArchitectService
from .serializers import VotesSerializer, SendVotesSerializer, CloseVotesSerializer, \
UserBanSerializer



class VotesTableView(APIView):
    permission_classes = [HasValidToken]

    def get(self, request):
        user = request.user
        votes = VoteService(user)

        serializer = VotesSerializer(votes.get_all_votes(), many = True)

        return Response(
            {
                "status": "OK",
                "notification": "All votes",
                "data": serializer.data
            },
            status = status.HTTP_200_OK
        )



class SendVoteView(APIView):
    permission_classes = [HasValidToken]

    def post(self, request):

        user = request.user

        serializer = SendVotesSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        send = SendVoteService()

        if send.user_already_voted(user_id = user.id, vote_id = serializer.validated_data["id"]):
            return Response(
                {
                    "status": "ALREADY_VOTED",
                    "notification": "User already voted",
                },
                status = status.HTTP_400_BAD_REQUEST
            )

        result = send.commit_choice(
            user.id,
            serializer.validated_data["id"],
            serializer.validated_data["choice"]
        )

        if result:

            return Response(
                {
                    "status": "OK",
                    "notification": f"{result}",
                },
                status = status.HTTP_200_OK
            )


        return Response(
            {
                "status": "CONFLICT",
                "notification": "Invalid request",
            },
            status=status.HTTP_409_CONFLICT
        )



class PromotionPermissionView(APIView):
    permission_classes = [HasValidToken]

    def get(self, request):
        user = request.user
        service = PermissionService(user)

        if service.has_promote_permission():
            return Response(
                {
                    "status": "OK",
                    "notification": "User has permission to create promotion vote"
                },
                status = status.HTTP_200_OK
            )

        return Response(
            {
                "status": "REFUSED",
                "notification": "User role has not expired yet"
            },
            status = status.HTTP_403_FORBIDDEN
        )



class BanPermissionView(APIView):
    permission_classes = [HasValidToken]

    def get(self, request):
        user = request.user

        service = PermissionService(user)

        if service.has_ban_permission():
            serializer = UserBanSerializer(service.get_all_users_for_ban(), many = True)

            return Response(
                {
                    "status": "OK",
                    "notification": "User has permission to create ban vote",
                    "data" : serializer.data
                }
            )

        return Response(
            {
                "status": "REFUSED",
                "notification": "User has not inquisitor role"
            },
            status = status.HTTP_403_FORBIDDEN
        )



class UserPromoteView(APIView):
    permission_classes = [HasValidToken]

    def patch(self, request):
        user = request.user

        service = UserPromoteService(user)

        if service.create_vote():
            return Response(
                {
                    "status": "OK",
                    "notification": "Vote for user promotion was created"
                },
                status = status.HTTP_200_OK
            )

        return Response(
            {
                "status": "BAD_REQUEST",
                "notification": "User has already created vote for promotion"
            },
            status = status.HTTP_400_BAD_REQUEST
        )



class UserBanView(APIView):
    permission_classes = [HasValidToken]

    def patch(self, request):

        serializer = UserBanSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        service = UserBanService(**serializer.validated_data)

        if service.create_vote():
            return Response(
                {
                    "status" : "OK",
                    "notification": "Vote for ban user was created"
                },
                status = status.HTTP_200_OK
            )

        return Response(
            {
                "status": "BAD_REQUEST",
                "notification": "User has already created vote for ban selected user"
            },
            status = status.HTTP_400_BAD_REQUEST
        )



class CloseActiveExpiredVotesView(APIView):

    def patch(self, request):

        serializer = CloseVotesSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        try:
            if VoteService.close_votes(date = serializer.validated_data["date_of_end"]):
                return Response(
                    {
                        "status": "OK",
                        "notification": "All active votes was closed"
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                {
                    "status": "BAD_REQUEST",
                    "notification": "Error to close votes"
                },
                status = status.HTTP_400_BAD_REQUEST
            )

        except ZeroDivisionError:
            return Response(
                {
                    "status": "OK",
                    "notification": "No users votes"
                },
                status=status.HTTP_200_OK
            )



class InquisitorManagementView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inquisitor_management_service = InquisitorManagementService()


    def patch(self, request):

        if self.inquisitor_management_service.appoint_inquisitor_role():
            return Response(
                {
                    "status": "OK",
                    "notification": "The inquisitorial role was established"
                },
                status = status.HTTP_200_OK
            )

        return Response(
            {
                "status": "BAD_REQUEST",
                "notification": "Error to appoint inquisitor role"
            },
            status = status.HTTP_400_BAD_REQUEST
        )


    def delete(self, request):

        if self.inquisitor_management_service.remove_inquisitor_role():
            return Response(
                {
                    "status": "OK",
                    "notification": "The inquisitorial role was blocked"
                },
                status = status.HTTP_200_OK
            )

        return Response(
            {
                "status": "BAD_REQUEST",
                "notification": "Error to block inquisitor role"
            },
            status = status.HTTP_400_BAD_REQUEST
        )



class UserArchitectView(APIView):

    def delete(self, request):

        service = UserArchitectService()

        if service.delete_architect():
            return Response(
                {
                    "status": "OK",
                    "notification": "User with architect role was deleted"
                },
                status = status.HTTP_200_OK
            )

        return Response(
            {
                "status": "BAD_REQUEST",
                "notification" : "There is no architect or date has not expired yet"
            },
            status = status.HTTP_400_BAD_REQUEST
        )
