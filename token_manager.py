#!/usr/bin/env python3
"""
多服务器Dropbox Token管理器
"""
import requests
import json
import os
from datetime import datetime

class MultiServerTokenManager:
    def __init__(self):
        self.app_key = 'bl4dllhus4upqu9'
        self.app_secret = '54ppgfj4c2hagos'
        self.token_file = 'shared_token.json'
        self.config_file = 'dropbox_config.py'
    
    def get_current_token(self):
        """获取当前有效的token"""
        # 先检查共享token文件
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                if self.validate_token(data['access_token']):
                    return data
            except:
                pass
        
        # 检查本地配置
        try:
            from dropbox_config import DROPBOX_CONFIG
            token = DROPBOX_CONFIG['access_token']
            if self.validate_token(token):
                return {'access_token': token, 'source': 'local_config'}
        except:
            pass
        
        return None
    
    def validate_token(self, access_token):
        """验证token是否有效"""
        try:
            response = requests.post(
                'https://api.dropboxapi.com/2/users/get_current_account',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_new_token_from_code(self, auth_code):
        """使用授权码获取新token"""
        token_url = "https://api.dropboxapi.com/oauth2/token"
        
        data = {
            'code': auth_code,
            'grant_type': 'authorization_code',
            'client_id': self.app_key,
            'client_secret': self.app_secret
        }
        
        try:
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                if self.validate_token(token_data['access_token']):
                    # 保存token
                    self.save_token(token_data)
                    self.update_config(token_data['access_token'])
                    return token_data
            return None
        except:
            return None
    
    def save_token(self, token_data):
        """保存token到共享文件"""
        try:
            token_info = {
                'access_token': token_data['access_token'],
                'created_at': datetime.now().isoformat(),
                'expires_in': token_data.get('expires_in')
            }
            with open(self.token_file, 'w') as f:
                json.dump(token_info, f, indent=2)
        except:
            pass
    
    def update_config(self, access_token):
        """更新本地配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    content = f.read()
                
                import re
                new_content = re.sub(
                    r"'access_token':\s*'[^']*'",
                    f"'access_token': '{access_token}'",
                    content
                )
                
                with open(self.config_file, 'w') as f:
                    f.write(new_content)
                return True
        except:
            pass
        return False
    
    def get_auth_url(self):
        """获取授权URL"""
        return f"https://www.dropbox.com/oauth2/authorize?client_id={self.app_key}&response_type=code&token_access_type=offline"

def main():
    import sys
    manager = MultiServerTokenManager()
    
    if len(sys.argv) == 1:
        print("用法:")
        print("  python3 token_manager.py auth            # 获取授权URL")
        print("  python3 token_manager.py update <code>   # 使用授权码更新token")
        print("  python3 token_manager.py validate        # 验证当前token")
        
    elif sys.argv[1] == 'auth':
        print("🔐 获取Dropbox授权")
        print("请访问以下URL进行授权:")
        print(manager.get_auth_url())
        print("授权后，使用以下命令更新token:")
        print("python3 token_manager.py update <authorization_code>")
        
    elif sys.argv[1] == 'update' and len(sys.argv) == 3:
        auth_code = sys.argv[2]
        result = manager.get_new_token_from_code(auth_code)
        if result:
            print("🎉 Token更新成功!")
        else:
            print("❌ Token更新失败")
            
    elif sys.argv[1] == 'validate':
        token = manager.get_current_token()
        if token:
            print("✅ Token有效")
        else:
            print("❌ Token无效，需要重新获取")

if __name__ == "__main__":
    main() 