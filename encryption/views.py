import os

from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from enums.http_code_enums import ResponseCode
from utils.response import ApiResponse

@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_key(request):
    # 从文件中读取公钥
    #获取项目根目录
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(path+"\\public_key.pem", "r") as f:
        public_key = f.read()
    return ApiResponse.success(data={"public_key": public_key.__str__()}, msg='登录成功', code=ResponseCode.SUCCESS)
