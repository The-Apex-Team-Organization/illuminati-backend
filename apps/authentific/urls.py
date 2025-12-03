from django.urls import path
from .views import RegisterView, LoginView, EntryView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('entry/', EntryView.as_view(), name='entry'),
]