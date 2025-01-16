import time

from django.shortcuts import render
import os


import hashlib
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()
# 微信公众平台的 Token
TOKEN = os.getenv('WECHAT_TOKEN')  # 你可以在 settings.py 中配置 Token


def verify_signature(signature, timestamp, nonce):
    """
    验证微信服务器的签名，确保是微信发来的请求
    """
    token = TOKEN
    temp_list = [token, timestamp, nonce]
    temp_list.sort()
    temp_str = ''.join(temp_list)
    temp_str = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
    return temp_str == signature


@csrf_exempt  # 取消 CSRF 验证（因为微信是外部请求）
def wechat(request):
    if request.method == 'GET':
        print('GET request')
        # 微信验证
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')

        # 验证签名
        if verify_signature(signature, timestamp, nonce):
            return HttpResponse(echostr)  # 返回 echostr 完成验证
        else:
            return HttpResponse('Invalid signature')

    elif request.method == 'POST':
        print('POST request')
        # 处理微信消息
        if request.body:
            print(request.body)
            xml_str = request.body
            msg = ET.fromstring(xml_str)
            to_user = msg.find("ToUserName").text  # 接收方帐号
            from_user = msg.find("FromUserName").text  # 发送方帐号
            msg_type = msg.find("MsgType").text  # 消息类型
            event=msg.find("Event").text
            event_key=msg.find("EventKey").text
            print(to_user, from_user, msg_type)
            # 示例: 文本消息
            if msg_type == "text":
                content = msg.find("Content").text  # 消息内容
                return_text = f"收到你的消息: {content}"
                response = generate_text_response(from_user, to_user, return_text)
                return HttpResponse(response, content_type="application/xml")

            elif msg_type == "SCAN":
                response = generate_text_response(from_user, to_user, '欢迎登录蓝果汁AI')

            else:
                return HttpResponse('success')


def generate_text_response(to_user, from_user, content):
    """
    生成文本消息的响应XML
    """
    response = f"""
    <xml>
        <ToUserName>{to_user}</ToUserName>
        <FromUserName>{from_user}</FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType>text</MsgType>
        <Content>{content}</Content>
    </xml>
    """
    return response
