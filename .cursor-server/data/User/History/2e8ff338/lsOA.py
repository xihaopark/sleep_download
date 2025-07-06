#!/usr/bin/env python3
"""
使用App Key和Secret获取新的长期Dropbox token
"""

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

def get_long_lived_token():
    # 用户提供的App Key和Secret
    app_key = "bl4dllhus4upqu9"
    app_secret = "54ppgfj4c2hagos"
    
    print("=== 获取长期Dropbox Token ===\n")
    
    try:
        # 创建OAuth2流程，设置为offline模式获取refresh token
        auth_flow = DropboxOAuth2FlowNoRedirect(
            app_key, 
            app_secret,
            token_access_type='offline'  # 重要：获取可刷新的长期token
        )
        
        # 获取授权URL
        authorize_url = auth_flow.start()
        
        print("请按以下步骤操作：")
        print("1. 复制下面的URL到浏览器中打开：")
        print(f"\n{authorize_url}\n")
        print("2. 在浏览器中授权应用访问你的Dropbox")
        print("3. 授权后会显示一个授权码")
        print("4. 将授权码粘贴到下面：\n")
        
        # 获取用户输入的授权码
        auth_code = input("请输入授权码: ").strip()
        
        if not auth_code:
            print("❌ 授权码不能为空!")
            return None
        
        # 完成OAuth流程获取tokens
        oauth_result = auth_flow.finish(auth_code)
        
        access_token = oauth_result.access_token
        refresh_token = oauth_result.refresh_token
        
        print(f"\n✅ 成功获取长期tokens!")
        print(f"Access Token: {access_token}")
        if refresh_token:
            print(f"Refresh Token: {refresh_token}")
        
        # 测试新token是否有效
        print("\n正在测试新token...")
        dbx = dropbox.Dropbox(access_token)
        account = dbx.users_get_current_account()
        print(f"✅ Token测试成功! 账户: {account.name.display_name}")
        
        # 获取存储空间信息
        space_usage = dbx.users_get_space_usage()
        used = space_usage.used
        allocated = space_usage.allocation.get_individual().allocated
        
        print(f"存储使用情况:")
        print(f"- 已使用: {used / (1024**3):.2f} GB")
        print(f"- 总容量: {allocated / (1024**3):.2f} GB")
        print(f"- 可用空间: {(allocated - used) / (1024**3):.2f} GB")
        
        # 保存tokens到文件
        token_info = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'app_key': app_key,
            'app_secret': app_secret
        }
        
        # 保存到配置文件
        with open('dropbox_config.txt', 'w') as f:
            f.write(f"ACCESS_TOKEN={access_token}\n")
            if refresh_token:
                f.write(f"REFRESH_TOKEN={refresh_token}\n")
            f.write(f"APP_KEY={app_key}\n")
            f.write(f"APP_SECRET={app_secret}\n")
        
        print(f"\n💾 Token信息已保存到 dropbox_config.txt")
        
        return token_info
        
    except Exception as e:
        print(f"❌ 获取token失败: {e}")
        return None

if __name__ == "__main__":
    result = get_long_lived_token()
    if result:
        print("\n🎉 Token获取成功! 现在可以更新项目中的所有脚本了。")
    else:
        print("\n❌ Token获取失败，请检查App Key和Secret是否正确。") 