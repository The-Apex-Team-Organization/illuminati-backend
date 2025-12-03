from .models import Record


def get_all_records():
    return Record.objects.all()
