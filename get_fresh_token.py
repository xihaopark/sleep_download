#!/usr/bin/env python3
"""
快速获取新的Dropbox访问令牌
"""
import requests
import json
from urllib.parse import urlencode
import webbrowser
import sys

# 从配置文件读取App Key和Secret
try:
    from dropbox_config import DROPBOX_CONFIG
    APP_KEY = 'bl4dllhus4upqu9'
    APP_SECRET = '54ppgfj4c2hagos'
except:
    print("请先设置App Key和Secret")
    sys.exit(1)

def get_new_token():
    """获取新的访问令牌"""
    
    # 1. 生成授权URL
    auth_url = f"https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&response_type=code&token_access_type=offline"
    
    print("🔐 获取新的Dropbox访问令牌")
    print("=" * 50)
    print()
    print("📋 请按以下步骤操作:")
    print("1. 复制下面的URL到浏览器:")
    print()
    print(auth_url)
    print()
    print("2. 登录Dropbox并授权应用")
    print("3. 复制重定向URL中的authorization code")
    print("4. 粘贴到下面的输入框")
    print()
    
    # 2. 获取授权码
    auth_code = input("请输入authorization code: ").strip()
    
    if not auth_code:
        print("❌ 授权码不能为空")
        return None
    
    # 3. 交换访问令牌
    token_url = "https://api.dropboxapi.com/oauth2/token"
    
    data = {
        'code': auth_code,
        'grant_type': 'authorization_code',
        'client_id': APP_KEY,
        'client_secret': APP_SECRET
    }
    
    try:
        print("🔄 正在获取访问令牌...")
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            refresh_token = token_data.get('refresh_token')
            
            print("✅ 成功获取新的访问令牌!")
            print()
            print("📝 新的访问令牌:")
            print(f"access_token = '{access_token}'")
            
            if refresh_token:
                print(f"refresh_token = '{refresh_token}'")
            
            # 4. 测试新令牌
            print()
            print("🧪 测试新令牌...")
            test_response = requests.post(
                'https://api.dropboxapi.com/2/users/get_current_account',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if test_response.status_code == 200:
                user_info = test_response.json()
                print(f"✅ 令牌有效! 用户: {user_info['name']['display_name']}")
                
                # 5. 更新配置文件
                print()
                print("🔄 更新配置文件...")
                update_config(access_token, refresh_token)
                
                return access_token
            else:
                print(f"❌ 令牌测试失败: {test_response.status_code}")
                return None
                
        else:
            print(f"❌ 获取令牌失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def update_config(access_token, refresh_token=None):
    """更新配置文件"""
    try:
        # 读取现有配置
        with open('dropbox_config.py', 'r') as f:
            content = f.read()
        
        # 更新access_token
        import re
        new_content = re.sub(
            r"'access_token':\s*'[^']*'",
            f"'access_token': '{access_token}'",
            content
        )
        
        # 如果有refresh_token，也更新它
        if refresh_token:
            if "'refresh_token'" in new_content:
                new_content = re.sub(
                    r"'refresh_token':\s*'[^']*'",
                    f"'refresh_token': '{refresh_token}'",
                    new_content
                )
            else:
                # 添加refresh_token
                new_content = new_content.replace(
                    "'upload_folder': '/Sleep_Data'",
                    f"'upload_folder': '/Sleep_Data',\n    'refresh_token': '{refresh_token}'"
                )
        
        # 写回文件
        with open('dropbox_config.py', 'w') as f:
            f.write(new_content)
        
        print("✅ 配置文件已更新")
        
    except Exception as e:
        print(f"❌ 更新配置文件失败: {e}")
        print("请手动更新dropbox_config.py文件中的access_token")

if __name__ == "__main__":
    token = get_new_token()
    if token:
        print()
        print("🎉 完成! 现在可以重新启动下载上传程序了")
        print("运行: python3 sleep_data_wget_manager.py")
    else:
        print("❌ 获取令牌失败，请重试") 