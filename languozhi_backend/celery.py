from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置 Django 的默认配置模块为 'my_django_project.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'languozhi_backend.settings')

# 实例化 Celery
app = Celery('languozhi')

# 使用 Celery 配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动加载所有注册到 'tasks' 模块中的任务
app.autodiscover_tasks()


app.autodiscover_tasks()