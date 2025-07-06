#!/usr/bin/env python3
"""
快速修复Dropbox token
"""
import requests
import sys

def exchange_code_for_token(auth_code):
    """用授权码换取访问令牌"""
    APP_KEY = 'bl4dllhus4upqu9'
    APP_SECRET = '54ppgfj4c2hagos'
    
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
            
            # 测试令牌
            test_response = requests.post(
                'https://api.dropboxapi.com/2/users/get_current_account',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if test_response.status_code == 200:
                print("✅ 令牌有效!")
                
                # 更新配置文件
                update_config(access_token)
                return True
            else:
                print(f"❌ 令牌测试失败: {test_response.status_code}")
                return False
                
        else:
            print(f"❌ 获取令牌失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def update_config(access_token):
    """更新配置文件"""
    try:
        with open('dropbox_config.py', 'r') as f:
            content = f.read()
        
        import re
        new_content = re.sub(
            r"'access_token':\s*'[^']*'",
            f"'access_token': '{access_token}'",
            content
        )
        
        with open('dropbox_config.py', 'w') as f:
            f.write(new_content)
        
        print("✅ 配置文件已更新")
        
    except Exception as e:
        print(f"❌ 更新配置文件失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 quick_token_fix.py <authorization_code>")
        print()
        print("1. 先访问: https://www.dropbox.com/oauth2/authorize?client_id=bl4dllhus4upqu9&response_type=code&token_access_type=offline")
        print("2. 授权后复制URL中的code参数")
        print("3. 运行: python3 quick_token_fix.py <code>")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    if exchange_code_for_token(auth_code):
        print("🎉 Token更新完成! 现在可以重新启动程序了")
    else:
        print("❌ Token更新失败") 