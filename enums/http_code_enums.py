from enum import Enum

class ResponseCode(Enum):
    # 全局状态码
    SUCCESS = 0  # 操作成功
    ERROR = -1  # 操作失败
    PARAMS_MISSING = -2  # 参数缺失或无效

    # 验证码相关状态码
    CAPTCHA_ERROR = 1001  # 验证码错误
    CAPTCHA_INVALID = 1002  # 验证码无效或过期

    # 用户认证相关状态码
    INVALID_CREDENTIALS = 2001  # 用户名或密码错误
    USER_DISABLED = 2002  # 用户被禁用
    USER_NOT_FOUND = 2003  # 用户不存在
    USER_ALREADY_EXISTS = 2004  # 用户已存在

    # 其他业务状态码
    PERMISSION_DENIED = 3001  # 权限不足
    SERVER_ERROR = 5000  # 服务器内部错误

    def describe(self):
        """
        返回状态码的描述信息。
        """
        descriptions = {
            self.SUCCESS: "操作成功",
            self.ERROR: "操作失败",
            self.PARAMS_MISSING: "参数缺失或无效",
            self.CAPTCHA_ERROR: "验证码错误",
            self.CAPTCHA_INVALID: "验证码无效或过期",
            self.INVALID_CREDENTIALS: "用户名或密码错误",
            self.USER_DISABLED: "用户被禁用",
            self.USER_NOT_FOUND: "用户不存在",
            self.USER_ALREADY_EXISTS: "用户已存在",
            self.PERMISSION_DENIED: "权限不足",
            self.SERVER_ERROR: "服务器内部错误",
        }
        return descriptions.get(self, "未知错误")
