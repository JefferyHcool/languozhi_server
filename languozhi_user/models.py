import uuid

from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class LGZUserManager(BaseUserManager):
    def create_user(self, username, phone_number, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field is required")
        if not phone_number:
            raise ValueError("The Phone Number field is required")

        # 使用 phone_number 来初始化 user
        user = self.model(username=username, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class LGZUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=36, unique=True, blank=True, null=True)  # 自定义 ID 字段
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(null=True, blank=True)  # 设置 email 字段可以为空
    password_hash = models.CharField(max_length=255, null=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True)
    role = models.CharField(max_length=20, default='teacher',choices=[('admin', 'Admin'), ('teacher', 'Teacher'), ('student', 'Student')])
    permissions = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    wechat_openid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    wechat_unionid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    wechat_nickname = models.CharField(max_length=50, null=True, blank=True)
    wechat_avatar = models.TextField(null=True, blank=True)
    is_wechat_user = models.BooleanField(default=False)
    invite_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    invited_by = models.CharField(max_length=20, null=True, blank=True)
    invite_time = models.DateTimeField(null=True, blank=True)
    invite_used_count = models.IntegerField(default=0)
    invite_max_usage = models.IntegerField(null=True, blank=True)
    login_count = models.IntegerField(default=0)
    activity_score = models.IntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = LGZUserManager()
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # 如果没有手动设置 user_id，生成一个新的 UUID
        if not self.user_id:
            self.user_id ='LGZ'+ str(uuid.uuid4()).replace('-', '')  # 这里使用 UUID 作为示例，你可以根据自己的需求更改规则
        if not self.role:
            self.role = 'teacher'
        super(LGZUser, self).save(*args, **kwargs)