from django.shortcuts import render

def home(request):
    return render(request, "frontend/index.html")

def login_view(request):
    return render(request, "frontend/login.html")

def register_view(request):
    return render(request, "frontend/register.html")

def forgot_password_view(request):
    return render(request, "frontend/forgot_password.html")

def reset_password_view(request):
    return render(request, "frontend/reset_password.html")

def read_view(request, book_id, page_number):
    return render(request, "frontend/read.html", {"book_id": book_id, "page_number": page_number})

def favorites_view(request):
    return render(request, "frontend/favorites.html")