import base64
from io import BytesIO

from django.shortcuts import render
from rest_framework.permissions import AllowAny

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

from enums.http_code_enums import ResponseCode
from languozhi_user.serializers import UserSerializer
from languozhi_user.services.userServices import UserService
from utils import get_client_ip
from utils.captcha_style import CaptchaService
from utils.encryption import load_private_key, decrypt_data
from utils.response import ApiResponse

User = get_user_model()
user_service = UserService(User)


class CaptchaAPIView(APIView):
    """
    返回验证码图片和对应的 key
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # 生成验证码的文本
        captcha_text = CaptchaStore.generate_key()
        captcha_instance = CaptchaStore.objects.get(hashkey=captcha_text)

        # 使用自定义生成器生成验证码图片
        generator = CaptchaService()
        captcha_image=generator.generate_captcha(captcha_instance.challenge)

        encoded = base64.b64encode(captcha_image.read()).decode('utf-8')
        data={
            "captcha_key": captcha_instance.hashkey,
            "captcha_image": f"data:image/png;base64,{encoded}",
        }
        return ApiResponse.success(data=data,code=ResponseCode.SUCCESS)


class LoginOrRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.data
        captcha_key = payload.get('captcha_key')
        captcha_value = payload.get('captcha_value')
        password = request.data.get('password')
        account = payload.get('account')

        try:
            if not account or not password:
                return ApiResponse.error(code=ResponseCode.PARAMS_MISSING)

            if not captcha_key or not captcha_value:
                return ApiResponse.error(code=ResponseCode.CAPTCHA_INVALID)
            payload['password'] = decrypt_data(password)
            captcha_value = decrypt_data(captcha_value)
            print(password,captcha_value)
            try:
                captcha = CaptchaStore.objects.get(hashkey=captcha_key)
                if captcha.response != captcha_value.lower():
                    return ApiResponse.error(code=ResponseCode.CAPTCHA_ERROR)
                captcha.delete()  # 验证成功后删除验证码
            except CaptchaStore.DoesNotExist:
                return ApiResponse.error(code=ResponseCode.CAPTCHA_INVALID)

            payload['last_login_ip'] = get_client_ip(request)
            user = user_service.loginOrRegister(payload)  # 获取模型实例
            if user:
                # 生成 JWT 的 RefreshToken
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)  # 获取 Access Token
                user_data = UserSerializer(user).data  # 序列化用户数据以便返回
                data = {
                    'user_info': user_data,
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                }
                return ApiResponse.success(data=data, msg='登录成功', code=ResponseCode.SUCCESS)

            return Response({'msg': '登录失败账号或密码错误', 'data': None, 'code': 200})
        except Exception as e:
            return ApiResponse.error( msg=e.__str__(), code=ResponseCode.ERROR)
