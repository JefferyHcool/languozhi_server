from languozhi_user.serializers import UserSerializer
import datetime

from utils import generate_verification_code, generate_random_password
from utils.encryption import load_private_key


class UserService:
    def __init__(self, user_model):
        self.user_model = user_model
        self.user_model.objects = user_model.objects

    # user_service.py

    def loginWithPhoneNumber(self, payload):
        '''
        用户登录接口V2
        :param payload
        :return: 成功返回用户模型实例，失败返回None
        '''
        user = None
        phone_number = payload['phone_number']
        last_login_ip = payload['last_login_ip']
        print("phone_number:", phone_number)
        if phone_number:
            user = self.user_model.objects.filter(phone_number=phone_number).first()
            if user:
                user.last_login = datetime.datetime.now()
                user.last_login_ip = payload['last_login_ip']
                user.login_count += 1
                user.save()
                return user  # 直接返回模型实例，而不是序列化后的字典
            print("用户不存在")
        user_data = {'username': phone_number, 'password': generate_random_password(), 'login_count': 1,
                     'phone_number': phone_number,
                     'last_login_ip': last_login_ip, 'last_login': datetime.datetime.now()}
        print("us", user_data)
        serializer = UserSerializer(data=user_data)
        print(serializer)
        if serializer.is_valid():
            user = serializer.save()
            return user  # 直接返回模型实例，而不是序列化后的字典
        print("错误：", serializer.errors)
        return None

    def loginOrRegister(self, payload):
        '''
        用户登录接口V1
        :param payload
        :return: 成功返回用户模型实例，失败返回None
        '''
        print(type(payload))

        user = None
        account = payload['account']
        password = payload['password']
        last_login_ip = payload['last_login_ip']
        if account:
            user = self.user_model.objects.filter(username=account).first()
        if not user:
            user = self.user_model.objects.filter(phone_number=account).first()

        if user:
            if user.check_password(password):
                user.last_login = datetime.datetime.now()
                user.last_login_ip = last_login_ip
                user.login_count += 1
                user.save()

                return user  # 直接返回模型实例，而不是序列化后的字典
            else:
                return None

        # 用户不存在时，自动注册
        user_data = {'username': account, 'password': password, 'login_count': 1, 'phone_number': account,
                     'last_login_ip': last_login_ip, 'last_login': datetime.datetime.now()}
        serializer = UserSerializer(data=user_data)
        print(serializer)
        if serializer.is_valid():
            user = serializer.save()
            return user  # 直接返回模型实例，而不是序列化后的字典
        print("错误：", serializer.errors)
        return None

    def send_msg(self, phone_number):
        '''
        发送短信验证码
        :param phone_number: 手机号
        :return: 成功返回True，失败返回False
        '''
        from utils.aliyun_sms import AliyunSMS
        sms = AliyunSMS()
        sign_name = "蓝果汁"  # 替换为申请的短信签名
        template_code = "SMS_477470104"  # 替换为申请的短信模板 Code
        template_param = {"code": generate_verification_code()}  # 短信模板中的参数

        result = sms.send_sms(phone_number, template_code, template_param)
        print("res", result)
        if result and result['code'] == 'OK':
            sms.save_verification_code(phone_number, template_param['code'])
        code = sms.get_verification_code(phone_number)
        print(code)
        if code:
            return True
        return False
