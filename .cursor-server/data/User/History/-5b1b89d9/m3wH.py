#!/usr/bin/env python3
"""
Dropbox Authentication Helper
帮助获取长期有效的Dropbox access token
"""

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
import sys

def get_long_lived_token():
    """
    获取长期有效的Dropbox token
    """
    print("=== Dropbox Long-lived Token Generator ===\n")
    
    # 你需要在Dropbox App Console中获取这些信息
    print("首先，你需要在Dropbox App Console中获取以下信息：")
    print("1. 访问: https://www.dropbox.com/developers/apps")
    print("2. 创建或选择你的应用")
    print("3. 在Settings页面找到 'App key' 和 'App secret'\n")
    
    app_key = input("请输入你的App Key: ").strip()
    app_secret = input("请输入你的App Secret: ").strip()
    
    if not app_key or not app_secret:
        print("❌ App Key和App Secret不能为空!")
        return None
    
    try:
        # 创建OAuth2流程
        auth_flow = DropboxOAuth2FlowNoRedirect(
            app_key, 
            app_secret,
            token_access_type='offline'  # 这个很重要！设置为offline获取长期token
        )
        
        # 获取授权URL
        authorize_url = auth_flow.start()
        print(f"\n请在浏览器中打开以下URL进行授权：")
        print(f"{authorize_url}")
        print("\n授权后，你会看到一个授权码")
        
        # 获取授权码
        auth_code = input("请输入授权码: ").strip()
        
        if not auth_code:
            print("❌ 授权码不能为空!")
            return None
        
        # 完成OAuth流程
        oauth_result = auth_flow.finish(auth_code)
        
        access_token = oauth_result.access_token
        refresh_token = oauth_result.refresh_token
        
        print(f"\n✅ 成功获取tokens!")
        print(f"Access Token: {access_token}")
        if refresh_token:
            print(f"Refresh Token: {refresh_token}")
            print("\n🔄 Refresh Token可以用来刷新过期的Access Token")
        
        # 测试token
        print("\n正在测试token...")
        dbx = dropbox.Dropbox(access_token)
        account = dbx.users_get_current_account()
        print(f"✅ Token有效! 账户: {account.name.display_name}")
        
        # 保存到文件
        with open('dropbox_tokens.txt', 'w') as f:
            f.write(f"ACCESS_TOKEN={access_token}\n")
            if refresh_token:
                f.write(f"REFRESH_TOKEN={refresh_token}\n")
            f.write(f"APP_KEY={app_key}\n")
            f.write(f"APP_SECRET={app_secret}\n")
        
        print(f"\n💾 Tokens已保存到 dropbox_tokens.txt")
        
        return access_token
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def refresh_access_token():
    """
    使用refresh token刷新access token
    """
    print("=== 刷新Access Token ===\n")
    
    try:
        with open('dropbox_tokens.txt', 'r') as f:
            lines = f.readlines()
            tokens = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    tokens[key] = value
        
        app_key = tokens.get('APP_KEY')
        app_secret = tokens.get('APP_SECRET')
        refresh_token = tokens.get('REFRESH_TOKEN')
        
        if not all([app_key, app_secret, refresh_token]):
            print("❌ 缺少必要的token信息")
            return None
        
        # 使用refresh token获取新的access token
        dbx = dropbox.Dropbox(app_key=app_key, app_secret=app_secret, oauth2_refresh_token=refresh_token)
        dbx.refresh_access_token()
        
        new_access_token = dbx._oauth2_access_token
        print(f"✅ 新的Access Token: {new_access_token}")
        
        # 更新文件
        tokens['ACCESS_TOKEN'] = new_access_token
        with open('dropbox_tokens.txt', 'w') as f:
            for key, value in tokens.items():
                f.write(f"{key}={value}\n")
        
        print("💾 新token已保存")
        return new_access_token
        
    except FileNotFoundError:
        print("❌ 找不到 dropbox_tokens.txt 文件")
        return None
    except Exception as e:
        print(f"❌ 刷新失败: {e}")
        return None

def main():
    print("选择操作：")
    print("1. 获取新的长期token")
    print("2. 刷新现有token")
    print("3. 退出")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    if choice == '1':
        get_long_lived_token()
    elif choice == '2':
        refresh_access_token()
    elif choice == '3':
        print("退出")
    else:
        print("无效选择")

if __name__ == "__main__":
    main() 