from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

from .models import User

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("username", "email")


class CustomAuthenticationForm(AuthenticationForm):
    pass

