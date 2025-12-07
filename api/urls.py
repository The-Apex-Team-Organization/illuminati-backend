from django.urls import path, include

urlpatterns = [
    path("authentific/", include("apps.authentific.urls")),
    path("users/", include("apps.users.urls")),
    path("records/", include("apps.records.urls")),
    path("snapshot/", include("apps.snapshot.urls")),
    path("password/", include("apps.entry_password.urls")),
    path("votes/", include("apps.votes.urls")),
    path("hall_of_fame/", include("apps.hall_of_fame.urls")),
]
