"""
URL configuration for languozhi_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from languozhi_user.views import CustomTokenRefreshView

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenVerifyView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    # 刷新 Access Token
    path('api/auth/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    # 验证 Token 是否有效
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/users/', include('languozhi_user.urls')),  # 将用户相关的路由包含进来
    path('captcha/', include('captcha.urls')),  # 添加这一行
    path('api/encryption/', include('encryption.urls')),
]
