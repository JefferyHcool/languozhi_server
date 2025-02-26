# -*- coding=utf-8
import datetime

from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import sys
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


class TencentCOSUploader:
    def __init__(self):
        # 1. 设置用户属性, 包括 secret_id, secret_key, region 等。
        self.secret_id = os.environ['TENCENT_SECRET_ID']  # 用户的 SecretId
        self.secret_key = os.environ['TENCENT_SECRET_KEY']  # 用户的 SecretKey
        self.region = os.environ['REGION']  # 用户的 region
        self.bucket = os.environ['BUCKET_NAME']  # COS 的 Bucket
        self.token = None  # 临时密钥的 Token
        self.scheme = 'https'  # 指定使用 http/https 协议来访问 COS

        # 初始化 CosConfig 和 CosS3Client
        self.config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Token=self.token,
            Scheme=self.scheme
        )
        self.client = CosS3Client(self.config)

    def remove_local_file(self,local_file_path):
        os.remove(local_file_path)

    import datetime
    from qcloud_cos import CosConfig, CosS3Client

    def generate_presigned_url(self,file_key: str, expires_in: int = 3600) -> str:
        """
        生成腾讯云 COS 临时访问 URL，有效期 expires_in 秒
        """
        cos_client =self.client

        signed_url = cos_client.get_presigned_url(
            Method='GET',
            Bucket=self.bucket,
            Key=file_key,
            Expired=int(datetime.datetime.now().timestamp()) + expires_in  # 过期时间
        )

        return signed_url

    def upload_file(self, key, local_file_path, enable_md5=False, progress_callback=None):
        """
        使用高级接口上传文件，不重试，不使用断点续传功能。

        :param key: 上传到 COS 的文件名
        :param local_file_path: 本地文件路径
        :param enable_md5: 是否启用 MD5 校验
        :param progress_callback: 上传进度回调函数
        :return: 上传响应
        """
        try:
            response = self.client.upload_file(
                Bucket=self.bucket,
                Key=key,
                LocalFilePath=local_file_path,
                EnableMD5=enable_md5,
                progress_callback=progress_callback
            )
            return response
        except (CosClientError, CosServiceError) as e:
            print(f"Upload failed: {e}")
            return None

    def upload_file_with_retry(self, key, local_file_path, max_retries=10):
        """
        使用高级接口断点续传，失败重试时不会上传已成功的分块。

        :param key: 上传到 COS 的文件名
        :param local_file_path: 本地文件路径
        :param max_retries: 最大重试次数
        :return: 上传响应
        """
        for i in range(max_retries):
            try:
                response = self.client.upload_file(
                    Bucket=self.bucket,
                    Key=key,
                    LocalFilePath=local_file_path
                )
                return response
            except (CosClientError, CosServiceError) as e:
                print(f"Attempt {i + 1} failed: {e}")
                if i == max_retries - 1:
                    print("Max retries reached. Upload failed.")
                    return None


# 示例用法
