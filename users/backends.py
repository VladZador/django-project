from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


User = get_user_model()


class PhoneModelBackend(ModelBackend):

    def authenticate(self, request, phone=None, password=None, **kwargs):
        if phone is None or password is None:
            return
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password) \
                    and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and user.is_phone_valid
