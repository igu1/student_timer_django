import calendar
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordChangeView,
    PasswordResetConfirmView,
)
from .forms import (
    RegistrationForm,
    LoginForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
    UserPasswordChangeForm,
)
from django.contrib.auth import logout
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import FormView
from .models import StudentStudyDate, StudentStudyTime, Quote
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
from django.db.models import Sum, ExpressionWrapper, F
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time, timedelta
import google.generativeai as genai


def premium(request):
    if request.method == "POST":
        if request.user.profile:
            request.user.profile.premium_user = True
            request.user.profile.save()
            print(request.user.profile.premium_user)
            return JsonResponse({"success": True})


@login_required(login_url="login")
def timer(request):
    base_hours = int(request.GET.get("hs", 1))
    base_minutes = int(request.GET.get("ms", 0))
    base_seconds = int(request.GET.get("ss", 0))

    if request.method == "POST":
        data = json.loads(request.body)
        base_time_delta = timedelta(
            hours=base_hours, minutes=base_minutes, seconds=base_seconds
        )
        time_delta = timedelta(
            hours=data["hours"], minutes=data["minutes"], seconds=data["seconds"]
        )
        total_seconds = time_delta.total_seconds()
        spent_hours = int(total_seconds // 3600)
        spent_minutes = int((total_seconds % 3600) // 60)
        spent_seconds = int(total_seconds % 60)
        spent_time_delta = timedelta(
            hours=spent_hours, minutes=spent_minutes, seconds=spent_seconds
        )
        remaining_time_delta = base_time_delta - spent_time_delta
        remaining_hours = int(remaining_time_delta.total_seconds() // 3600)
        remaining_minutes = int((remaining_time_delta.total_seconds() % 3600) // 60)
        remaining_seconds = int(remaining_time_delta.total_seconds() % 60)
        spent_time = time(remaining_hours, remaining_minutes, remaining_seconds)
        study_date, _ = StudentStudyDate.objects.get_or_create(
            user=request.user, date=datetime.now()
        )
        study_time_obj = StudentStudyTime.objects.create(
            study=study_date,
            time=spent_time,
        )
        return JsonResponse({"success": True})

    return render(
        request,
        "pages/timer.html",
        {
            "hours": base_hours,
            "minutes": base_minutes,
            "seconds": base_seconds,
            "quote": Quote.get_random_quote() or "Keep Clam, Stay Focused",
        },
    )


def format_timedelta(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


def get_study_time_range(user, start_date, end_date):
    dates = StudentStudyDate.objects.filter(
        user=user, date__range=[start_date, end_date]
    )
    times = StudentStudyTime.objects.filter(study__in=dates)
    total_time = sum(
        (time.time.hour * 3600 + time.time.minute * 60 + time.time.second)
        for time in times
    )
    return timedelta(seconds=total_time)


def get_total_study_hours(user):
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()

    dates = StudentStudyDate.objects.filter(
        user=user, date__range=[start_date, end_date]
    )

    times = StudentStudyTime.objects.filter(study__in=dates)

    total_seconds = sum(
        (time.time.hour * 3600 + time.time.minute * 60 + time.time.second)
        for time in times
    )

    total_hours = total_seconds // 3600  # Calculate total hours

    return total_hours


@login_required(login_url="login")
def index(request):
    return render(
        request,
        "pages/set-timer.html",
        {"username": request.GET.get("username") or None},
    )


@login_required(login_url="login")
def report(request):
    today = datetime.now()
    last_week_start = today - timedelta(days=today.weekday() + 7)
    last_week_end = today - timedelta(days=today.weekday() + 1)
    this_week_start = today - timedelta(days=today.weekday())
    this_week_end = today + timedelta(days=6 - today.weekday())
    this_month_start = today.replace(day=1)
    this_month_end = today.replace(day=1, month=today.month % 12 + 1) - timedelta(
        days=1
    )

    last_week_timedelta = get_study_time_range(
        request.user, last_week_start, last_week_end
    )
    this_week_timedelta = get_study_time_range(
        request.user, this_week_start, this_week_end
    )
    this_month_timedelta = get_study_time_range(
        request.user, this_month_start, this_month_end
    )
    today_timedelta = get_study_time_range(
        request.user, today, today + timedelta(days=1)
    )
    last_week_hours = format_timedelta(last_week_timedelta)
    this_week_hours = format_timedelta(this_week_timedelta)
    this_month_hours = format_timedelta(this_month_timedelta)
    today_hours = format_timedelta(today_timedelta)

    this_week_days = (this_week_end - this_week_start).days + 1
    this_week_avg_timedelta = this_week_timedelta / this_week_days
    this_week_avg_hours = format_timedelta(this_week_avg_timedelta)

    weeks_in_month = 4
    week_times = []
    for i in range(weeks_in_month):
        start_date = this_month_start + timedelta(weeks=i)
        end_date = start_date + timedelta(weeks=1) - timedelta(days=1)
        week_time = get_study_time_range(request.user, start_date, end_date)
        total_week_minutes = week_time.total_seconds() // 60
        week_times.append(int(total_week_minutes))

    months_in_year = 9
    month_times = []
    month_names = []
    for i in range(months_in_year):
        month = today.month - i
        year = today.year - (month <= 0)
        month = (month - 1) % 12 + 1
        start_date = today.replace(day=1, month=month, year=year)
        end_date = start_date.replace(day=calendar.monthrange(year, month)[1])
        month_time = get_study_time_range(request.user, start_date, end_date)
        total_month_minutes = month_time.total_seconds() // 60
        month_times.append(int(total_month_minutes))
        month_names.append(calendar.month_name[month])

    month_times.reverse()
    month_names.reverse()

    return render(
        request,
        "pages/index.html",
        {
            "today": today_hours,
            "last_week": last_week_hours,
            "this_week": this_week_hours,
            "this_month": this_month_hours,
            "this_week_avg": this_week_avg_hours,
            "week_times": week_times,
            "month_times": month_times,
            "month_names": month_names,
        },
    )


def leaderboard(request):
    users_readed = []
    today = datetime.now()
    users = request.user.profile.friends.all()
    for user in users:
        today_timedelta = get_study_time_range(user, today, today + timedelta(days=1))
        today_hours = format_timedelta(today_timedelta)
        users_readed.append((user, today_hours))
    users_readed.sort(key=lambda x: x[1], reverse=True)
    return render(request, "pages/leaderboard.html", {"users_readed": users_readed})


def profile(request):
    total_hours_of_study = get_total_study_hours(request.user)
    request.user.profile.score = total_hours_of_study
    request.user.profile.save()
    return render(request, "pages/profile.html", {"user": request.user})


def ask(request):
    context = {}
    if request.method == "POST":
        data = []
        genai.configure(api_key="AIzaSyAE-6xV3UHMTfi-nGj-VFYHElz3rB-fPos")
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            "make maximum questions and answer should be in the given data also answers about: "
            + request.POST["datas"]
        )
        data = ""
        for chunk in response:
            data = chunk.text.replace("\n", "<br>").replace("**", "<br>")
        context = {"data": data}

    return render(request, "pages/ask-questions.html", context)


def friends(request):

    return render(
        request,
        "pages/friends.html",
        {"users": User.objects.all().exclude(id=request.user.id)},
    )


def add_friend(request, id):
    if User.objects.get(id=id) not in request.user.profile.friends.all():
        request.user.profile.friends.add(User.objects.get(id=id))
    else:
        request.user.profile.friends.remove(User.objects.get(id=id))
    return redirect("friends")


# AIzaSyAE-6xV3UHMTfi-nGj-VFYHElz3rB-fPos


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        super().form_valid(form)
        username = form.cleaned_data.get("username")
        return redirect(reverse("index") + f"?username={username}")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            print("Account created successfully!")
            return redirect("/accounts/login/")
        else:
            print("Register failed!")
    else:
        form = RegistrationForm()

    context = {"form": form}
    return render(request, "accounts/register.html", context)


def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")


class UserPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = UserPasswordChangeForm
