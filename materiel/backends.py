from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

# ModelBackend personnalisé pour permettre l'authentification d'un utilisateur par son username ou son email.
class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

        return None
