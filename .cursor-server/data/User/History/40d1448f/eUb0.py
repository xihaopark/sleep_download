#!/usr/bin/env python3
"""
跨服务器Token同步脚本
支持通过GitHub、共享文件系统等方式同步token
"""
import requests
import json
import os
import subprocess
import time
from datetime import datetime

class TokenSyncManager:
    def __init__(self):
        self.token_file = 'shared_token.json'
        self.backup_file = 'token_backup.json'
        self.github_repo = 'xihaopark/sleep_download'  # 你的GitHub仓库
        
    def sync_via_github(self):
        """通过GitHub同步token"""
        try:
            print("🔄 通过GitHub同步token...")
            
            # 1. 拉取最新代码
            result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Git拉取成功")
                
                # 2. 检查是否有新的token文件
                if os.path.exists(self.token_file):
                    with open(self.token_file, 'r') as f:
                        token_data = json.load(f)
                    
                    # 3. 验证token
                    if self.validate_token(token_data['access_token']):
                        print("✅ 从GitHub获取到有效token")
                        
                        # 4. 更新本地配置
                        self.update_local_config(token_data['access_token'])
                        return True
                    else:
                        print("❌ GitHub上的token已过期")
                        return False
                else:
                    print("⚠️  GitHub上没有找到token文件")
                    return False
            else:
                print(f"❌ Git拉取失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ GitHub同步失败: {e}")
            return False
    
    def push_token_to_github(self, token_data):
        """推送token到GitHub"""
        try:
            print("📤 推送token到GitHub...")
            
            # 1. 保存token到文件
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # 2. 备份
            with open(self.backup_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # 3. Git提交
            subprocess.run(['git', 'add', self.token_file], check=True)
            subprocess.run(['git', 'commit', '-m', f'🔐 更新Dropbox token - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            print("✅ Token已推送到GitHub")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 推送失败: {e}")
            return False
    
    def sync_via_shared_file(self, shared_path):
        """通过共享文件系统同步token"""
        try:
            shared_token_file = os.path.join(shared_path, self.token_file)
            
            if os.path.exists(shared_token_file):
                print(f"🔄 从共享路径同步token: {shared_path}")
                
                # 复制共享文件到本地
                import shutil
                shutil.copy2(shared_token_file, self.token_file)
                
                # 验证token
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                
                if self.validate_token(token_data['access_token']):
                    print("✅ 共享文件中的token有效")
                    self.update_local_config(token_data['access_token'])
                    return True
                else:
                    print("❌ 共享文件中的token已过期")
                    return False
            else:
                print(f"⚠️  共享路径中没有找到token文件: {shared_path}")
                return False
                
        except Exception as e:
            print(f"❌ 共享文件同步失败: {e}")
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
            config_file = 'dropbox_config.py'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                
                import re
                new_content = re.sub(
                    r"'access_token':\s*'[^']*'",
                    f"'access_token': '{access_token}'",
                    content
                )
                
                with open(config_file, 'w') as f:
                    f.write(new_content)
                
                print("✅ 本地配置已更新")
                return True
        except Exception as e:
            print(f"❌ 更新本地配置失败: {e}")
        return False
    
    def create_sync_script(self):
        """创建定时同步脚本"""
        script_content = '''#!/bin/bash
# 定时Token同步脚本
# 每5分钟检查一次token状态

while true; do
    echo "$(date): 检查token状态..."
    
    # 尝试GitHub同步
    python3 sync_token_across_servers.py github
    
    # 如果失败，尝试其他方法
    if [ $? -ne 0 ]; then
        echo "$(date): GitHub同步失败，尝试其他方法..."
        # 这里可以添加其他同步方法
    fi
    
    # 等待5分钟
    sleep 300
done
'''
        
        with open('auto_sync_token.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('auto_sync_token.sh', 0o755)
        print("✅ 自动同步脚本已创建: auto_sync_token.sh")

def main():
    """主函数"""
    import sys
    
    sync_manager = TokenSyncManager()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 sync_token_across_servers.py github              # 从GitHub同步")
        print("  python3 sync_token_across_servers.py push <auth_code>    # 获取新token并推送到GitHub")
        print("  python3 sync_token_across_servers.py shared <path>       # 从共享文件系统同步")
        print("  python3 sync_token_across_servers.py create-script       # 创建自动同步脚本")
        return
    
    command = sys.argv[1]
    
    if command == 'github':
        success = sync_manager.sync_via_github()
        if success:
            print("🎉 GitHub同步成功!")
        else:
            print("❌ GitHub同步失败")
    
    elif command == 'push' and len(sys.argv) == 3:
        auth_code = sys.argv[2]
        
        # 获取新token
        from token_manager import MultiServerTokenManager
        manager = MultiServerTokenManager()
        token_data = manager.get_new_token_from_code(auth_code)
        
        if token_data:
            # 推送到GitHub
            success = sync_manager.push_token_to_github(token_data)
            if success:
                print("🎉 Token已更新并推送到GitHub!")
                print("其他服务器现在可以通过 'python3 sync_token_across_servers.py github' 同步")
            else:
                print("❌ 推送到GitHub失败")
        else:
            print("❌ 获取新token失败")
    
    elif command == 'shared' and len(sys.argv) == 3:
        shared_path = sys.argv[2]
        success = sync_manager.sync_via_shared_file(shared_path)
        if success:
            print("🎉 共享文件同步成功!")
        else:
            print("❌ 共享文件同步失败")
    
    elif command == 'create-script':
        sync_manager.create_sync_script()
    
    else:
        print("❌ 未知命令")

if __name__ == "__main__":
    main() 