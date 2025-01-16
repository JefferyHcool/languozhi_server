# wechat/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('wechat/', views.wechat, name='wechat'),  # 微信消息接收接口
]
