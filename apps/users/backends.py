from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Permite autenticarse con email o nombre de usuario."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # Buscar por email primero, luego por username
        user = (
            User.objects.filter(email__iexact=username).first()
            or User.objects.filter(username__iexact=username).first()
        )

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
