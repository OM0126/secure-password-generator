from django.urls import path
from .views import (
    IndexView, GeneratePasswordView, ClearHistoryView,
    LoginView, LogoutView
)

app_name = "password_generator"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("generate/", GeneratePasswordView.as_view(), name="generate"),
    path("clear-history/", ClearHistoryView.as_view(), name="clear_history"),
    

    path("login/", LoginView.as_view(), name="login"),

    path("logout/", LogoutView.as_view(), name="logout"),
]
