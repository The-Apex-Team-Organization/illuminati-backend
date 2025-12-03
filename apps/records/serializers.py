from rest_framework import serializers
from .models import Record, RecordActivityUser


class RecordActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordActivityUser
        fields = ["id", "user_id", "record_id", "like_status"]
        read_only_fields = ["id", "user_id", "record_id"]


class RecordSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True, default=0)
    liked_by_user = serializers.BooleanField(read_only=True, default=False)

    img_path = serializers.CharField(read_only=True)
    description = serializers.CharField(required=False, allow_blank=True)
    additional_info = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Record
        fields = [
            "id",
            "name",
            "x",
            "y",
            "type",
            "description",
            "img_path",
            "additional_info",
            "likes_count",
            "liked_by_user",
        ]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)

            for field_name in existing - allowed:
                self.fields.pop(field_name)
