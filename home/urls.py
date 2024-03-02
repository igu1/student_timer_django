from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("timer/", views.timer, name="timer"),
    path("report/", views.report, name="report"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("profile/", views.profile, name="profile"),
    path("ask/", views.ask, name="ask"),
    path("friends/", views.friends, name="friends"),
    path("add_friend/<int:id>/", views.add_friend, name="add_friend"),
    path("premium/", views.premium, name="premium"),
    path("accounts/login/", views.UserLoginView.as_view(), name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/register/", views.register, name="register"),
]
