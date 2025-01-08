# users/urls.py
from django.urls import path
from .views import LoginOrRegisterAPIView, CaptchaAPIView, SendSMSCode, LoginWithPhoneNumberAPIView

urlpatterns = [
    path('auth/captcha/', CaptchaAPIView.as_view(), name='captcha'),
    path('auth/login/', LoginOrRegisterAPIView.as_view(), name='login_or_register'),
    path('auth/login/sms', SendSMSCode.as_view(), name='login_sms'),
    path('auth/login_with_phone', LoginWithPhoneNumberAPIView.as_view(), name='login_with_phone'),

]
