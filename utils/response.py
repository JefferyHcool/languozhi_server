from rest_framework import status
from rest_framework.response import Response
from enums.http_code_enums import ResponseCode

class ApiResponse:
    @staticmethod
    def success(data=None, msg=None, code=ResponseCode.SUCCESS):
        """
        返回成功响应
        :param data: 返回的数据
        :param msg: 提示信息
        :param code: 状态码（枚举类型，默认成功为 ResponseCode.SUCCESS）
        """
        if isinstance(code, ResponseCode):
            code_value = code.value
            msg = msg or code.describe()
        else:
            code_value = code
            msg = msg or "操作成功"

        return Response({
            "code": code_value,
            "msg": msg,
            "data": data,
        })

    @staticmethod
    def error(msg=None, code=ResponseCode.ERROR, data=None):
        """
        返回错误响应
        :param msg: 错误提示信息
        :param code: 状态码（枚举类型，默认失败为 ResponseCode.ERROR）
        :param data: 返回的数据（通常为空）
        """
        if isinstance(code, ResponseCode):
            code_value = code.value
            msg = msg or code.describe()
        else:
            code_value = code
            msg = msg or "操作失败"

        return Response({
            "code": code_value,
            "msg": msg,
            "data": data,
        })

    @staticmethod
    def no_auth_response(msg=None, code=ResponseCode.ERROR, data=None):
        """
        未登录响应
        """
        if isinstance(code, ResponseCode):
            code_value = code.value
            msg = msg or code.describe()
        else:
            code_value = code
            msg = msg or "操作失败"

        return Response({
            "code":code.value,
            "msg": code.describe(),
            "data": None,

        },status=status.HTTP_401_UNAUTHORIZED)