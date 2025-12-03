from rest_framework import serializers
from .models import HallOfFame


class HallOfFameSerializer(serializers.ModelSerializer):
    class Meta:
        model = HallOfFame
        fields = ["id", "username"]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
