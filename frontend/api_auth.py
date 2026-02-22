from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
import json


@ensure_csrf_cookie
@require_GET
def csrf(request):
    # Só para garantir que o cookie csrftoken existe
    return JsonResponse({"ok": True})


@require_GET
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False}, status=401)

    u = request.user
    return JsonResponse({
        "authenticated": True,
        "id": u.id,
        "username": u.get_username(),
        "email": u.email,
        "is_staff": u.is_staff,
        "is_superuser": u.is_superuser,
    })


@require_POST
def login_view(request):
    # Aceita JSON {username/password} ou form-data
    username = ""
    password = ""

    ct = (request.headers.get("Content-Type") or "").lower()
    if "application/json" in ct:
        try:
            data = json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            data = {}
        username = (data.get("username") or data.get("email") or "").strip()
        password = (data.get("password") or "").strip()
    else:
        username = (request.POST.get("username") or request.POST.get("email") or "").strip()
        password = (request.POST.get("password") or "").strip()

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Credenciais inválidas."}, status=400)

    login(request, user)  # <-- cria sessão
    return JsonResponse({"ok": True})


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"ok": True})