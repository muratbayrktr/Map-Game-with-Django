from django.shortcuts import render, redirect, resolve_url

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm, CustomAuthenticationForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("home")
    template_name = "registration/signup.html"


from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import UserToken
import uuid

def custom_login_view(request):
    form = CustomAuthenticationForm()

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            token, created = UserToken.objects.get_or_create(user=user)
            if created:
                token.token = uuid.uuid4().hex
                token.save()

            response = JsonResponse({"token": token.token})
            response.set_cookie(key='auth_token', value=token.token, httponly=True)
            request.session['auth_token'] = token.token
            print("Cookie set:", response.cookies)
            # Go to the home page
            return redirect(resolve_url("home"))
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

    return render(request, "registration/login.html", {"form": form})


def custom_logout_view(request):
    # Log out the user
    logout(request)

    # Clear the token from both the session and the cookie
    if 'auth_token' in request.session:
        del request.session['auth_token']
    response = JsonResponse({"message": "Logged out successfully"})
    response.delete_cookie('auth_token')

    return response
