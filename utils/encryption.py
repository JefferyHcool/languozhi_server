import os

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key


def generate_rsa_keys():
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 生成公钥
    public_key = private_key.public_key()

    # 保存私钥
    with open("../private_key.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # 保存公钥
    with open("../public_key.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


def load_private_key(private_key_path="../private_key.pem"):
    """
    加载私钥
    :param private_key_path: 私钥文件路径
    :return: 私钥对象
    """
    try:
        with open(private_key_path, "rb") as f:
            private_key = load_pem_private_key(f.read(), password=None)
        return private_key
    except Exception as e:
        raise ValueError(f"加载私钥失败: {e}")

def load_public_key(public_key_path="public_key.pem"):
    """
    加载公钥
    :param public_key_path: 公钥文件路径
    :return: 公钥对象
    """
    try:
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        with open(path+'\\'+public_key_path, "rb") as f:
            public_key = load_pem_public_key(f.read())
        return public_key
    except Exception as e:
        raise ValueError(f"加载公钥失败: {e}")
def decrypt_data(encrypted_data_base64, private_key_path="private_key.pem"):
    """
    解密加密数据
    :param encrypted_data_base64: Base64 格式的加密数据
    :param private_key_path: 私钥文件路径
    :return: 解密后的明文数据
    """
    try:
        # 加载私钥
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        private_key = load_private_key(path + '\\' + private_key_path)

        # 将 Base64 数据解码为字节
        import base64
        encrypted_data = base64.b64decode(encrypted_data_base64)

        # 解密数据
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_data.decode("utf-8")  # 返回解密后的明文字符串
    except Exception as e:
        raise ValueError(f"解密失败: {e}")

def encrypt_data(data, public_key_path="public_key.pem"):
    """
    使用公钥加密数据
    :param data: 需要加密的明文数据（字符串）
    :param public_key_path: 公钥文件路径
    :return: 加密后的数据（Base64 格式字符串）
    """
    try:
        # 加载公钥
        public_key = load_public_key(public_key_path)

        # 加密数据
        encrypted_data = public_key.encrypt(
            data.encode("utf-8"),  # 将字符串转换为字节
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # 将加密后的字节数据转换为 Base64 格式
        import base64
        return base64.b64encode(encrypted_data).decode("utf-8")
    except Exception as e:
        raise ValueError(f"加密失败: {e}")


password= encrypt_data("xjgr")
print(password)
print(decrypt_data(password))