from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from .forms import SimpleRegisterForm

def home(request):
    return render(request, "scheduler/home.html")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "scheduler/login.html", {"form": form})


def register_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SimpleRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account was created and you are logged in.")
            return redirect("home")
        messages.error(request, "Please fix the errors below.")
    else:
        form = SimpleRegisterForm()

    return render(request, "scheduler/register.html", {"form": form})


def logout_page(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect("home")
