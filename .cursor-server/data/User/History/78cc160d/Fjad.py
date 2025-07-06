#!/usr/bin/env python3
"""
加密敏感信息脚本
密码: 1871
"""

import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

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

def encrypt_data(data: str, password: str = "1871") -> str:
    """加密数据"""
    key = generate_key_from_password(password)
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()

def decrypt_data(encrypted_data: str, password: str = "1871") -> str:
    """解密数据"""
    key = generate_key_from_password(password)
    f = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted_data = f.decrypt(encrypted_bytes)
    return decrypted_data.decode()

def encrypt_config_file():
    """加密配置文件"""
    try:
        # 读取配置文件
        with open('dropbox_config.txt', 'r') as f:
            config_content = f.read()
        
        # 加密配置
        encrypted_config = encrypt_data(config_content)
        
        # 保存加密后的配置
        encrypted_data = {
            'encrypted_config': encrypted_config,
            'note': 'Use decrypt_sensitive.py with password 1871 to decrypt',
            'files': ['dropbox_config.txt']
        }
        
        with open('encrypted_config.json', 'w') as f:
            json.dump(encrypted_data, f, indent=2)
        
        print("✅ 配置文件已加密保存到 encrypted_config.json")
        return True
        
    except FileNotFoundError:
        print("❌ 找不到 dropbox_config.txt 文件")
        return False
    except Exception as e:
        print(f"❌ 加密失败: {e}")
        return False

def create_decrypt_script():
    """创建解密脚本"""
    decrypt_script = '''#!/usr/bin/env python3
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
'''
    
    with open('decrypt_sensitive.py', 'w') as f:
        f.write(decrypt_script)
    
    print("✅ 解密脚本已创建: decrypt_sensitive.py")

def main():
    print("=== 加密敏感信息 ===")
    print("密码: 1871")
    
    # 安装依赖
    try:
        import cryptography
        print("✅ cryptography 已安装")
    except ImportError:
        print("📦 正在安装 cryptography...")
        os.system("pip3 install cryptography")
    
    # 加密配置文件
    if encrypt_config_file():
        create_decrypt_script()
        print("\\n🔐 敏感信息已加密保护")
        print("📁 加密文件: encrypted_config.json")
        print("🔓 解密脚本: decrypt_sensitive.py")
        print("🔑 密码: 1871")
    else:
        print("❌ 加密失败")

if __name__ == "__main__":
    main() 