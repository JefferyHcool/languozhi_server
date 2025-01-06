import os

from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def get_public_key(request):
    # 从文件中读取公钥
    #获取项目根目录
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(path+"\\public_key.pem", "r") as f:
        public_key = f.read()
    return JsonResponse({"public_key": public_key})
