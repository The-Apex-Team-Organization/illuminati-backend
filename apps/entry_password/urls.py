from django.urls import path
from .views import EntryView

urlpatterns = [
    path('new_entry_password/', EntryView.as_view(), name='entry_password'),
]