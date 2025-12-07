from rest_framework import serializers


class VotesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    percent = serializers.FloatField()



class SendVotesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    choice = serializers.CharField()



class CloseVotesSerializer(serializers.Serializer):
    date_of_end = serializers.DateTimeField(
        input_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
        ],
        required = True
    )



class UserBanSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
