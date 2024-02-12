from django.urls import path

from .views import SignUpView, custom_login_view, custom_logout_view

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path('login/', custom_login_view, name='login'),
    path('logout/', custom_logout_view, name='logout')
]