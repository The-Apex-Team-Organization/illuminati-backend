from .models import Record, RecordActivityUser
from django.db.models import Count


def get_all_records():
    records = list(Record.objects.all())
    counts_qs = (
        RecordActivityUser.objects.filter(like_status=True)
        .values("record_id")
        .annotate(count=Count("id"))
    )
    counts = {row["record_id"]: row["count"] for row in counts_qs}

    for r in records:
        r.likes_count = counts.get(r.id, 0)
        r.liked_by_user = False
    return records


def create_record(data):
    record = Record.objects.create(**data)
    return record


def get_record_by_id(record_id, user_id=None):
    try:
        record = Record.objects.get(id=record_id)
    except Record.DoesNotExist:
        return None

    count = RecordActivityUser.objects.filter(
        record_id=record_id, like_status=True
    ).count()
    record.likes_count = count

    if user_id is not None:
        exists = RecordActivityUser.objects.filter(
            record_id=record_id, user_id=user_id, like_status=True
        ).exists()
        record.liked_by_user = exists
    else:
        record.liked_by_user = False

    return record


def like_record(user_id, record_id):
    try:
        Record.objects.get(id=record_id)
    except Record.DoesNotExist:
        return None

    RecordActivityUser.objects.update_or_create(
        user_id=user_id,
        record_id=record_id,
        defaults={"like_status": True},
    )

    likes_count = RecordActivityUser.objects.filter(
        record_id=record_id, like_status=True
    ).count()
    return {"likes_count": likes_count, "liked_by_user": True}


def unlike_record(user_id, record_id):
    RecordActivityUser.objects.filter(user_id=user_id, record_id=record_id).delete()
    likes_count = RecordActivityUser.objects.filter(
        record_id=record_id, like_status=True
    ).count()
    return {"likes_count": likes_count, "liked_by_user": False}


def erase_all_records():
    RecordActivityUser.objects.all().delete()
    Record.objects.all().delete()
