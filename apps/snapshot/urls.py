from django.urls import path
from .views import RecordsBackupView
from .views import RecordsRestoreView

urlpatterns = [
    path('download/', RecordsBackupView.as_view(), name='records_backup'),
    path('upload/', RecordsRestoreView.as_view(), name='records_restore'),
]