from languozhi_user.serializers import UserSerializer
import datetime

from utils.encryption import load_private_key


class UserService:
    def __init__(self, user_model):
        self.user_model = user_model
        self.user_model.objects = user_model.objects

    # user_service.py

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
        user_data = {'username': account, 'password': password,'login_count':1, 'phone_number': account,
                     'last_login_ip': last_login_ip, 'last_login': datetime.datetime.now()}
        serializer = UserSerializer(data=user_data)
        print(serializer)
        if serializer.is_valid():
            user = serializer.save()
            return user  # 直接返回模型实例，而不是序列化后的字典
        print("错误：", serializer.errors)
        return None
