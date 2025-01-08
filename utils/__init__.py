import random
import string


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_verification_code(length=6):
    """
    生成随机验证码
    :param length: 验证码长度
    :return: 随机验证码字符串
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def generate_random_password(length=8):
    """
    生成随机密码
    :param length: 密码长度
    :return: 随机密码字符串
    """
    characters = string.ascii_letters + string.digits
    password = ''.join([random.choice(characters) for _ in range(length)])
    return password
