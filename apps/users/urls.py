from django.urls import path

from .views import ChangePasswordView, CurrentUserView

urlpatterns = [
    path("me/", CurrentUserView.as_view(), name="user-me"),
    path("change-password/", ChangePasswordView.as_view(), name="user-change-password"),
]
