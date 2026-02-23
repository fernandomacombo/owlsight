from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=6, write_only=True)

    # Extras (opcionais) — só salva se você tiver Profile/fields
    phone = serializers.CharField(required=False, allow_blank=True, max_length=40)
    address = serializers.CharField(required=False, allow_blank=True, max_length=255)
    birth_year = serializers.IntegerField(required=False)

    def validate_username(self, value: str):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Username é obrigatório.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Este username já existe.")
        return value

    def validate_email(self, value: str):
        value = (value or "").strip().lower()
        if not value:
            raise serializers.ValidationError("Email é obrigatório.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        phone = validated_data.pop("phone", "")
        address = validated_data.pop("address", "")
        birth_year = validated_data.pop("birth_year", None)

        user = User(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        user.set_password(password)
        user.save()

        # Tenta guardar extras num Profile, se você tiver isso no projeto.
        # Não quebra se não existir.
        try:
            # Caso 1: você tem user.profile
            profile = getattr(user, "profile", None)
            if profile is not None:
                if hasattr(profile, "phone"):
                    profile.phone = phone
                if hasattr(profile, "address"):
                    profile.address = address
                if hasattr(profile, "birth_year") and birth_year is not None:
                    profile.birth_year = birth_year
                profile.save()
        except Exception:
            pass

        return user