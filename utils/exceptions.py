from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, AuthenticationFailed
from rest_framework.response import Response

from enums.http_code_enums import ResponseCode
from utils.response import ApiResponse


def custom_exception_handler(exc, context):
    """
    自定义异常处理器，用于统一处理返回格式
    """
    # 调用 DRF 的默认异常处理器
    response = exception_handler(exc, context)

    if response is not None:
        # 确保 exc.detail 是字典，避免 TypeError
        detail = exc.detail if isinstance(exc.detail, dict) else {"detail": str(exc)}

        # 打印调试信息（可删除）
        print('ex', detail)

        # 处理 Token 相关错误
        if detail.get('code') == 'token_not_valid':
            return ApiResponse.no_auth_response(code=ResponseCode.TOKEN_INVALID)

        return ApiResponse.error(msg=detail.get('detail', '未知错误'), code=response.status_code)

    # 处理未认证异常
    if isinstance(exc, NotAuthenticated):
        return ApiResponse.no_auth_response(code=ResponseCode.UNAUTHORIZED, msg="身份认证信息未提供")

    # 如果异常未被 DRF 捕获，返回标准 500 错误
    return ApiResponse.error(code=ResponseCode.ERROR, msg="Internal server error")