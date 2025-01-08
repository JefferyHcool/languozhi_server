from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, AuthenticationFailed
from rest_framework.response import Response

from enums.http_code_enums import ResponseCode
from utils.response import ApiResponse


def custom_exception_handler(exc, context):
    """
    自定义异常处理器，用于统一处理返回格式
    """
    # 首先调用默认的异常处理器
    response = exception_handler(exc, context)

    if response is not None:
        # 获取默认错误信息
        default_detail = str(exc.detail if hasattr(exc, 'detail') else exc)
        print('ex',exc.detail['code']=='token_not_valid')
        # 进一步判断是否是 Token 过期
        # 针对某些特定异常类型进行自定义处理

        if exc.detail['code']=='token_not_valid':
            return ApiResponse.no_auth_response(code=ResponseCode.TOKEN_INVALID)
        else:
            return ApiResponse.error(msg=default_detail, code=response.status_code)

    # 如果异常未被 DRF 的默认处理器捕获，直接返回一个标准化的 500 错误
    return ApiResponse.error(code=ResponseCode.ERROR, msg="Internal server error")
