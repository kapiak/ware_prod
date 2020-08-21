from django.urls import path

from assistant.users.views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
    user_email_exists,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
    path("exists/<str:email>", user_email_exists, name="user_email_exists"),
]
