from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="User name ou email",
        widget=forms.TextInput(attrs={
            "autocomplete": "username",
            "placeholder": "ex: fernando ou fernando@email.com",
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "placeholder": "••••••••",
        })
    )

    def clean(self):
        """
        Permite login com email:
        se o utilizador digitar algo com '@', tentamos encontrar o username pela email.
        """
        username = self.data.get("username", "").strip()
        if "@" in username:
            try:
                user = User.objects.get(email__iexact=username)
                # substitui o valor enviado para o auth padrão
                mutable = self.data.copy()
                mutable["username"] = user.get_username()
                self.data = mutable
            except User.DoesNotExist:
                # não revela se existe ou não, deixa o auth falhar normalmente
                pass

        return super().clean()