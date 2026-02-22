import json

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

User = get_user_model()


@require_GET
@ensure_csrf_cookie
def csrf_view(request):
    """
    Só para garantir que o cookie 'csrftoken' exista antes dos POSTs.
    O teu JS chama /api/csrf/ no ensureCsrf().
    """
    return JsonResponse({"ok": True})


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return {}


@require_POST
def login_view(request):
    """
    POST /api/auth/login/
    body: { username, password, remember }
    - aceita username OU email
    - usa sessão Django (cookie)
    """
    data = _json_body(request)
    username_or_email = (data.get("username") or "").strip()
    password = data.get("password") or ""
    remember = bool(data.get("remember"))

    if not username_or_email or not password:
        return JsonResponse({"error": "Preencha usuário/email e senha."}, status=400)

    # Permite login por email
    username = username_or_email
    if "@" in username_or_email:
        u = User.objects.filter(email__iexact=username_or_email).only("username").first()
        if u:
            username = u.username

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Usuário ou senha inválidos."}, status=401)

    if not user.is_active:
        return JsonResponse({"error": "Conta desativada."}, status=403)

    login(request, user)

    # Remember-me: sessão longa; sem remember: sessão expira ao fechar browser
    if remember:
        # Usa SESSION_COOKIE_AGE do settings (default 2 semanas) ou define aqui
        request.session.set_expiry(getattr(settings, "SESSION_COOKIE_AGE", 1209600))
    else:
        request.session.set_expiry(0)

    return JsonResponse({"ok": True})


@require_POST
def google_login_view(request):
    """
    POST /api/auth/google/
    body: { credential }  (ID token do Google Identity Services)
    - verifica o token e cria/loga o user
    """
    data = _json_body(request)
    credential = data.get("credential")

    if not credential:
        return JsonResponse({"error": "Credencial Google ausente."}, status=400)

    google_client_id = getattr(settings, "GOOGLE_CLIENT_ID", "") or ""
    if not google_client_id:
        return JsonResponse({"error": "GOOGLE_CLIENT_ID não configurado no servidor."}, status=500)

    # Verificação do token (requer google-auth)
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            audience=google_client_id,
        )
    except Exception:
        return JsonResponse({"error": "Token Google inválido."}, status=401)

    email = (idinfo.get("email") or "").strip().lower()
    email_verified = bool(idinfo.get("email_verified"))
    sub = idinfo.get("sub")  # ID único do Google

    if not email:
        return JsonResponse({"error": "Google não retornou email."}, status=400)
    if not email_verified:
        return JsonResponse({"error": "Email Google não verificado."}, status=401)
    if not sub:
        return JsonResponse({"error": "Google não retornou identificador."}, status=400)

    # Busca/cria usuário
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        # username único baseado no email
        base = email.split("@")[0]
        candidate = base
        i = 1
        while User.objects.filter(username=candidate).exists():
            i += 1
            candidate = f"{base}{i}"

        user = User.objects.create(
            username=candidate,
            email=email,
            first_name=(idinfo.get("given_name") or "")[:150],
            last_name=(idinfo.get("family_name") or "")[:150],
            is_active=True,
        )
        user.set_unusable_password()
        user.save()

    login(request, user)
    request.session.set_expiry(getattr(settings, "SESSION_COOKIE_AGE", 1209600))

    return JsonResponse({"ok": True})