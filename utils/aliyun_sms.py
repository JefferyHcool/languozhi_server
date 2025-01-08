import os
from typing import Dict
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util.client import Client as UtilClient

from languozhi_backend.settings import ALIYUN_SMS_ACCESS_KEY, ALIYUN_SMS_ACCESS_SECRET, ALIYUN_SMS_SIGN_NAME

from django.core.cache import cache

from utils import generate_verification_code


class AliyunSMS:
    def __init__(self):
        """
        初始化阿里云短信客户端
        :param access_key_id: 阿里云 Access Key ID
        :param access_key_secret: 阿里云 Access Key Secret
        """
        self.access_key_id = ALIYUN_SMS_ACCESS_KEY
        self.access_key_secret = ALIYUN_SMS_ACCESS_SECRET
        self.client = self.create_client()

    def create_client(self) -> Dysmsapi20170525Client:
        """
        创建阿里云短信服务客户端
        :return: Dysmsapi20170525Client
        """
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
        )
        config.endpoint = 'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    def send_sms(self, phone_number: str, template_code: str, template_param: Dict[str, str]) -> Dict:
        """
        发送短信
        :param phone_number: 目标手机号
        :param sign_name: 短信签名
        :param template_code: 短信模板代码
        :param template_param: 模板参数（如验证码等）
        :return: 返回阿里云短信服务的响应结果
        """
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=phone_number,
            sign_name=ALIYUN_SMS_SIGN_NAME,
            template_code=template_code,
            template_param=str(template_param),  # 必须是 JSON 字符串
        )
        try:
            # 调用发送短信的接口
            response = self.client.send_sms(send_sms_request)
            return {
                "code": response.body.code,
                "message": response.body.message,
                "request_id": response.body.request_id,
                "biz_id": response.body.biz_id if response.body.biz_id else None,
            }
        except Exception as error:
            # 处理异常
            print(f"短信发送失败：{error}")
            return {
                "code": "Error",
                "message": str(error),
                "request_id": None,
                "biz_id": None,
            }



    def save_verification_code(self,phone_number: str, code: str, expire_time: int = 300):
        """
        保存验证码到 Redis
        :param phone_number: 手机号
        :param code: 验证码
        :param expire_time: 有效期（秒）
        """
        cache.set(f'sms_code_{phone_number}', code, expire_time)

    @staticmethod
    def get_verification_code(phone_number: str) -> str:
        """
        从 Redis 获取验证码
        :param phone_number: 手机号
        :return: 验证码
        """
        return cache.get(f'sms_code_{phone_number}')

    @staticmethod
    def delete_verification_code(phone_number: str):
        """
        从 Redis 删除验证码
        :param phone_number: 手机号
        """
        cache.delete(f'sms_code_{phone_number}')


