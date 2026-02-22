import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout

@ensure_csrf_cookie
@require_GET
def csrf(request):
    # Só para “setar” o csrftoken no cookie
    return JsonResponse({"ok": True})

@require_GET
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"is_authenticated": False}, status=200)

    u = request.user
    return JsonResponse({
        "is_authenticated": True,
        "id": u.id,
        "username": u.get_username(),
        "email": u.email or "",
        "is_staff": bool(u.is_staff),
        "is_superuser": bool(u.is_superuser),
    })

@require_POST
def login_view(request):
    # Espera JSON: {"username":"", "password":""}
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return JsonResponse({"detail": "Username e password são obrigatórios."}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"detail": "Credenciais inválidas."}, status=400)

    login(request, user)
    return JsonResponse({"ok": True})

@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"ok": True})