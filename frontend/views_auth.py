from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm

class OwlsightLoginView(LoginView):
    template_name = "frontend/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        remember = self.request.POST.get("remember")
        if remember:
            # 14 dias
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            # expira ao fechar
            self.request.session.set_expiry(0)

        messages.success(self.request, "Bem-vindo de volta.")

        nxt = self.request.POST.get("next") or self.request.GET.get("next") or settings.LOGIN_REDIRECT_URL
        if url_has_allowed_host_and_scheme(
            nxt,
            allowed_hosts={self.request.get_host()},
            require_https=not settings.DEBUG
        ):
            return redirect(nxt)
        return redirect(settings.LOGIN_REDIRECT_URL)

    def form_invalid(self, form):
        # mensagem genérica (não dizer se user existe)
        messages.error(self.request, "Não foi possível entrar. Verifica os dados e tenta novamente.")
        return super().form_invalid(form)


@require_POST
def owlsight_logout(request):
    logout(request)
    messages.info(request, "Sessão terminada.")
    return redirect(settings.LOGOUT_REDIRECT_URL)