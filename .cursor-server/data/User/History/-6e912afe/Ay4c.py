#!/usr/bin/env python3
"""
多服务器Dropbox Token管理器
支持token共享、自动刷新、集中管理
"""
import requests
import json
import time
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path

class MultiServerTokenManager:
    def __init__(self):
        self.app_key = 'bl4dllhus4upqu9'
        self.app_secret = '54ppgfj4c2hagos'
        self.token_file = 'shared_token.json'
        self.config_file = 'dropbox_config.py'
        self.lock = threading.Lock()
        
        # 服务器标识
        self.server_id = self.get_server_id()
        
        print(f"🖥️  服务器ID: {self.server_id}")
    
    def get_server_id(self):
        """获取服务器唯一标识"""
        try:
            # 使用主机名 + IP的组合
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return f"{hostname}_{ip.replace('.', '_')}"
        except:
            # 备用方案：使用时间戳
            return f"server_{int(time.time())}"
    
    def get_current_token(self):
        """获取当前有效的token"""
        with self.lock:
            # 1. 先检查本地token文件
            local_token = self.load_local_token()
            if local_token and self.validate_token(local_token['access_token']):
                return local_token
            
            # 2. 检查共享token文件
            shared_token = self.load_shared_token()
            if shared_token and self.validate_token(shared_token['access_token']):
                # 更新本地配置
                self.update_local_config(shared_token['access_token'])
                return shared_token
            
            # 3. 如果都无效，需要重新获取
            print("❌ 所有token都已过期，需要重新获取")
            return None
    
    def load_local_token(self):
        """从本地配置文件加载token"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    content = f.read()
                
                # 提取access_token
                import re
                match = re.search(r"'access_token':\s*'([^']+)'", content)
                if match:
                    return {
                        'access_token': match.group(1),
                        'source': 'local_config',
                        'server_id': self.server_id,
                        'updated_at': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"⚠️  读取本地配置失败: {e}")
        return None
    
    def load_shared_token(self):
        """从共享token文件加载token"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                return data
        except Exception as e:
            print(f"⚠️  读取共享token失败: {e}")
        return None
    
    def save_shared_token(self, token_data):
        """保存token到共享文件"""
        try:
            token_info = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in'),
                'created_at': datetime.now().isoformat(),
                'created_by': self.server_id,
                'last_validated': datetime.now().isoformat()
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(token_info, f, indent=2)
            
            print(f"✅ Token已保存到共享文件: {self.token_file}")
            return True
        except Exception as e:
            print(f"❌ 保存共享token失败: {e}")
            return False
    
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
    
    def update_local_config(self, access_token):
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
                
                print(f"✅ 本地配置已更新 (服务器: {self.server_id})")
                return True
        except Exception as e:
            print(f"❌ 更新本地配置失败: {e}")
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
            print("🔄 正在获取新的访问令牌...")
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # 验证新token
                if self.validate_token(token_data['access_token']):
                    print("✅ 新token获取成功并验证通过")
                    
                    # 保存到共享文件
                    self.save_shared_token(token_data)
                    
                    # 更新本地配置
                    self.update_local_config(token_data['access_token'])
                    
                    return token_data
                else:
                    print("❌ 新token验证失败")
                    return None
            else:
                print(f"❌ 获取token失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None
    
    def refresh_token_if_needed(self, refresh_token):
        """如果有refresh_token，尝试刷新"""
        if not refresh_token:
            return None
        
        token_url = "https://api.dropboxapi.com/oauth2/token"
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.app_key,
            'client_secret': self.app_secret
        }
        
        try:
            print("🔄 正在刷新访问令牌...")
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # 保存新token
                self.save_shared_token(token_data)
                self.update_local_config(token_data['access_token'])
                
                print("✅ Token刷新成功")
                return token_data
            else:
                print(f"❌ Token刷新失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 刷新请求失败: {e}")
            return None
    
    def sync_token_from_other_servers(self):
        """从其他服务器同步token"""
        # 这里可以实现从其他服务器拉取token的逻辑
        # 比如通过共享文件系统、数据库、或API
        pass
    
    def get_auth_url(self):
        """获取授权URL"""
        return f"https://www.dropbox.com/oauth2/authorize?client_id={self.app_key}&response_type=code&token_access_type=offline"
    
    def status_report(self):
        """生成状态报告"""
        print("=" * 60)
        print(f"🔐 多服务器Token管理器状态报告")
        print("=" * 60)
        print(f"服务器ID: {self.server_id}")
        print(f"共享Token文件: {self.token_file}")
        print(f"本地配置文件: {self.config_file}")
        print()
        
        # 检查当前token状态
        current_token = self.get_current_token()
        if current_token:
            print("✅ 当前Token状态: 有效")
            print(f"Token来源: {current_token.get('source', 'unknown')}")
            print(f"创建时间: {current_token.get('created_at', 'unknown')}")
            print(f"创建服务器: {current_token.get('created_by', 'unknown')}")
        else:
            print("❌ 当前Token状态: 无效或不存在")
        
        print("=" * 60)

def main():
    """主函数"""
    import sys
    
    manager = MultiServerTokenManager()
    
    if len(sys.argv) == 1:
        # 显示状态
        manager.status_report()
        print()
        print("用法:")
        print("  python3 token_manager.py status          # 查看状态")
        print("  python3 token_manager.py auth            # 获取授权URL")
        print("  python3 token_manager.py update <code>   # 使用授权码更新token")
        print("  python3 token_manager.py validate        # 验证当前token")
        print("  python3 token_manager.py sync            # 从其他服务器同步token")
        
    elif sys.argv[1] == 'status':
        manager.status_report()
        
    elif sys.argv[1] == 'auth':
        print("🔐 获取Dropbox授权")
        print("请访问以下URL进行授权:")
        print()
        print(manager.get_auth_url())
        print()
        print("授权后，使用以下命令更新token:")
        print("python3 token_manager.py update <authorization_code>")
        
    elif sys.argv[1] == 'update' and len(sys.argv) == 3:
        auth_code = sys.argv[2]
        result = manager.get_new_token_from_code(auth_code)
        if result:
            print("🎉 Token更新成功!")
            print("现在所有服务器都可以使用新的token了")
        else:
            print("❌ Token更新失败")
            
    elif sys.argv[1] == 'validate':
        token = manager.get_current_token()
        if token:
            print("✅ Token有效")
        else:
            print("❌ Token无效，需要重新获取")
            
    elif sys.argv[1] == 'sync':
        print("🔄 同步token...")
        manager.sync_token_from_other_servers()
        
    else:
        print("❌ 未知命令")

if __name__ == "__main__":
    main() 