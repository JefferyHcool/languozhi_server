import base64
import json
import os
import random
import time

import qrcode
import redis
import requests
from dotenv import load_dotenv
from PIL import Image
import io
def generate_qr_code_with_logo(data, logo_path='assets/logo.png', size=300):
    """
    生成带logo的二维码
    :param data: 二维码数据
    :param logo_path: logo图片路径
    :param size: 二维码大小
    :return: 二维码base64编码
    """
    try:
        # 创建二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 允许高容错率
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # 生成二维码图像
        qr_image = qr.make_image(fill='black', back_color='white').convert('RGBA')

        # 获取项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_full_path = os.path.join(base_dir, logo_path)

        # 打开logo图像并调整大小
        logo = Image.open(logo_full_path)
        logo_size = int(qr_image.size[0] / 4)  # 设置logo的大小为二维码宽度的1/5
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)  # 使用LANCZOS代替ANTIALIAS

        # 将logo粘贴到二维码中心
        qr_image.paste(logo, ((qr_image.size[0] - logo.size[0]) // 2, (qr_image.size[1] - logo.size[1]) // 2), logo)

        # 将二维码图像转换为Base64编码
        buffered = io.BytesIO()
        qr_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return 'data:image/png;base64,' + img_base64

    except Exception as e:
        print(f"生成二维码失败: {e}")
        return None
def generate_scene_id():
    '''
    场景值ID，临时二维码时为32位非0整型，永久二维码时最大值为100000（目前参数只支持1--100000）
    :return:
    '''
    data = ''
    for i in range(32):
        data += str(random.randint(1, 9))
    return data


def byte_to_image(byte_data, file_name="qrcode.png"):
    """
    将二进制数据转为图片并保存到本地
    """
    image = Image.open(io.BytesIO(byte_data))
    image.save(file_name)
    print(f"二维码已保存为 {file_name}")
    return file_name


class WechatService:
    def __init__(self):
        load_dotenv()
        self.app_id = os.getenv("WECHAT_APP_ID")
        self.app_secret = os.getenv("WECHAT_APP_SECRET")
        self.token_cache_key = "wechat_access_token"  # 存储到 Redis 的 key
        self.token_expiry_cache_key = "wechat_access_token_expiry"  # 存储过期时间的 key

        # 初始化 Redis 客户端
        self.redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=os.getenv('REDIS_PORT'),
                                              db=os.getenv('REDIS_DB'),
                                              decode_responses=True)

    def _get_access_token_from_api(self):
        """
        调用微信 API 获取新的 access_token
        """
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return data["access_token"], data["expires_in"]
            else:
                raise Exception(f"Failed to get access token: {data.get('errmsg')}")
        else:
            raise Exception(f"Request failed with status {response.status_code}")

    def get_access_token(self):
        """
        获取 access_token，如果过期则重新生成
        """
        access_token = self.redis_client.get(self.token_cache_key)
        expiry_time = self.redis_client.get(self.token_expiry_cache_key)

        # 检查 Redis 是否有存储的 access_token，且是否过期
        if access_token and expiry_time and time.time() < float(expiry_time):
            return access_token

        # 如果没有有效的 access_token，调用微信 API 获取新的 token
        new_access_token, expires_in = self._get_access_token_from_api()

        # 将新的 access_token 和过期时间存入 Redis
        self.redis_client.set(self.token_cache_key, new_access_token, ex=expires_in - 60)  # 提前 60 秒失效
        self.redis_client.set(self.token_expiry_cache_key, time.time() + expires_in - 60, ex=expires_in - 60)

        return new_access_token

    def create_ticket(self, access_token, expire_seconds=60):
        try:
            url = f'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={access_token}'

            data = {"expire_seconds": expire_seconds, "action_name": "QR_SCENE",
                    "action_info": {"scene": {"scene_id": generate_scene_id()}}}
            response = requests.post(url, json=data)
            if response.status_code == 200:
                if response.json().get("ticket"):

                    return (response.json().get("ticket"), response.json().get("url"), response.json().get("expire_seconds"),
                            generate_qr_code_with_logo(response.json().get("url")))
                else:
                    print(response.json())
                    return None
            else:
                print(response)
                return None
        except Exception as e:
            print('获取二维码失败', e)

    def create_qrcode(self, ticket):
        url = f'https://mp.weixin.qq.com/cgi-bin/showqrcode'
        params = {"ticket": ticket}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            if response.content:
                return response.content
            else:
                print(response.json())
                return None
    def create_qrcode(self):

        return generate_qr_code_with_logo("", "")

    def send_template_message(self,access_token, openid, data, url=None):
        template_id=os.getenv("WECHAT_TEMPLATE_ID")
        send_url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
        message = {
            "touser": openid,
            "template_id": template_id,
            "url": url,
            "data": data
        }
        response = requests.post(send_url, data=json.dumps(message))
        if response.status_code == 200:
            result = response.json()
            if result.get('errcode') == 0:
                print("Message sent successfully")
            else:
                print(f"Failed to send message: {result.get('errmsg')}")
        else:
            raise Exception("Failed to send message")

if __name__ == '__main__':
    wechat_service = WechatService()
    accssess_token = wechat_service.get_access_token()
    wechat_service.send_template_message(accssess_token,'ortcf5t5T9tczRlrDNgNo8TqEUx0', {"name":{"value":"测试"},"time":{"value":"2023-03-01 12:00:00"}})
    # import os
    #
    # print(os.getcwd().replace(r'\utils',''))
    # print(generate_qr_code_with_logo("http://weixin.qq.com/q/02LTzIVXKncvC1GzK8hD10"))