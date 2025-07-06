#!/usr/bin/env python3
"""
解密敏感信息脚本
使用密码: 1871
"""

import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key_from_password(password: str, salt: bytes = b'sleep_data_salt') -> bytes:
    """从密码生成加密密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def decrypt_data(encrypted_data: str, password: str) -> str:
    """解密数据"""
    key = generate_key_from_password(password)
    f = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted_data = f.decrypt(encrypted_bytes)
    return decrypted_data.decode()

def main():
    password = input("请输入密码: ").strip()
    
    try:
        # 读取加密配置
        with open('encrypted_config.json', 'r') as f:
            encrypted_data = json.load(f)
        
        # 解密配置
        config_content = decrypt_data(encrypted_data['encrypted_config'], password)
        
        # 保存解密后的配置
        with open('dropbox_config.txt', 'w') as f:
            f.write(config_content)
        
        print("✅ 配置文件已解密并保存到 dropbox_config.txt")
        print("现在可以运行项目了！")
        
    except Exception as e:
        print(f"❌ 解密失败: {e}")
        print("请检查密码是否正确")

if __name__ == "__main__":
    main()
