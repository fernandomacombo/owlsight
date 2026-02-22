from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func))

def superuser_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_superuser)(view_func))

@staff_required
def home(request):
    return render(request, "dashboard/home.html")

@staff_required
def books(request):
    return render(request, "dashboard/books.html")

@superuser_required
def users(request):
    return render(request, "dashboard/users.html")

@staff_required
def settings_view(request):
    return render(request, "dashboard/settings.html")