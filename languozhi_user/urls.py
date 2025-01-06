# users/urls.py
from django.urls import path
from .views import LoginOrRegisterAPIView, CaptchaAPIView

urlpatterns = [
    path('auth/captcha/', CaptchaAPIView.as_view(), name='captcha'),
    path('auth/login/', LoginOrRegisterAPIView.as_view(), name='login_or_register'),
]
