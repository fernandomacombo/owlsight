from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class RegisterAPIView(APIView):
    """
    POST /api/auth/register/
    Body:
      {
        "username": "fernando",
        "email": "a@b.com",
        "password": "123456",
        "first_name": "...",   (opcional)
        "last_name": "..."     (opcional)
      }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data or {}

        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()

        # ✅ validações básicas
        errors = {}
        if not username:
            errors["username"] = ["Username é obrigatório."]
        if not email:
            errors["email"] = ["Email é obrigatório."]
        if not password or len(password) < 6:
            errors["password"] = ["Senha deve ter no mínimo 6 caracteres."]

        if username and User.objects.filter(username__iexact=username).exists():
            errors["username"] = ["Este username já existe."]
        if email and User.objects.filter(email__iexact=email).exists():
            errors["email"] = ["Este email já está em uso."]

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # ✅ cria no DB
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        # nomes opcionais
        if hasattr(user, "first_name"):
            user.first_name = first_name
        if hasattr(user, "last_name"):
            user.last_name = last_name
        user.save()

        return Response(
            {
                "ok": True,
                "id": user.id,
                "username": user.username,
                "email": getattr(user, "email", "") or "",
            },
            status=status.HTTP_201_CREATED,
        )


class MeAPIView(APIView):
    """
    GET /api/auth/me/
    (útil para o read.html também)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response(
            {
                "id": u.id,
                "username": getattr(u, "username", "") or "",
                "email": getattr(u, "email", "") or "",
                "name": (f"{getattr(u,'first_name','') or ''} {getattr(u,'last_name','') or ''}").strip(),
            }
        )