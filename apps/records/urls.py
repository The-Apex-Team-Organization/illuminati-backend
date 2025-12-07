from django.urls import path
from .views import (
    RecordListView,
    RecordCreateView,
    RecordDetailView,
    RecordEraseView,
    LikeRecordView,
    UnlikeRecordView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("all", RecordListView.as_view(), name="records-all"),
    path("create", RecordCreateView.as_view(), name="records-create"),
    path("<int:record_id>", RecordDetailView.as_view(), name="records-detail"),
    path("erase", RecordEraseView.as_view(), name="records-erase"),
    path("<int:record_id>/like/", LikeRecordView.as_view(), name="records-like"),
    path("<int:record_id>/unlike/", UnlikeRecordView.as_view(), name="records-unlike"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
