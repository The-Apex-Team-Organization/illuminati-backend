from django.urls import path
from .views import HallOfFameListView, HallOfFameMessageView

urlpatterns = [
    path("", HallOfFameListView.as_view(), name="hall-of-fame-list"),
    path("send", HallOfFameMessageView.as_view(), name="hall-of-fame-send"),
]
