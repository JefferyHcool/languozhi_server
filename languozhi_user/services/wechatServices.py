import os

from utils.WechatService import WechatService


def get_qrcode_url():
    try:
        access_token = WechatService().get_access_token()
        ticket, url, expire_seconds,base64Data = WechatService().create_ticket(access_token)
        print(f"ticket:{ticket},url:{url},expire_seconds:{expire_seconds},base64Data:{base64Data}")
        if base64Data:

            return base64Data,expire_seconds
        return None
    except Exception as e:
        print(e)
        return None
