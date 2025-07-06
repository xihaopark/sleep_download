#!/usr/bin/env python3
"""
测试更新后的Dropbox token是否正常工作
"""

import dropbox
import sys

def test_updated_token():
    """测试新token的功能"""
    
    # 从配置文件读取token
    try:
        with open('dropbox_config.txt', 'r') as f:
            lines = f.readlines()
            config = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
        
        access_token = config.get('ACCESS_TOKEN')
        if not access_token:
            print("❌ 配置文件中没有找到ACCESS_TOKEN")
            return False
            
    except FileNotFoundError:
        print("❌ 找不到 dropbox_config.txt 文件")
        return False
    
    print("=== 测试更新后的Dropbox Token ===\n")
    
    try:
        # 初始化Dropbox客户端
        dbx = dropbox.Dropbox(access_token)
        
        # 测试1: 获取账户信息
        print("🔍 测试1: 获取账户信息...")
        account = dbx.users_get_current_account()
        print(f"✅ 账户名: {account.name.display_name}")
        print(f"✅ 邮箱: {account.email}")
        
        # 测试2: 列出根目录文件
        print("\n🔍 测试2: 列出Dropbox根目录...")
        try:
            result = dbx.files_list_folder("")
            print(f"✅ 根目录包含 {len(result.entries)} 个项目")
            for entry in result.entries[:5]:  # 只显示前5个
                entry_type = "📁" if hasattr(entry, 'id') and entry.id else "📄"
                print(f"   {entry_type} {entry.name}")
            if len(result.entries) > 5:
                print(f"   ... 还有 {len(result.entries) - 5} 个项目")
        except Exception as e:
            print(f"⚠️  列出文件时出错: {e}")
        
        # 测试3: 创建测试文件夹
        print("\n🔍 测试3: 创建测试文件夹...")
        test_folder = "/sleep_data_test"
        try:
            dbx.files_create_folder_v2(test_folder)
            print(f"✅ 成功创建文件夹: {test_folder}")
        except dropbox.exceptions.ApiError as e:
            if "path_lookup/conflict" in str(e):
                print(f"✅ 文件夹已存在: {test_folder}")
            else:
                print(f"⚠️  创建文件夹失败: {e}")
        
        # 测试4: 上传测试文件
        print("\n🔍 测试4: 上传测试文件...")
        test_content = "这是一个测试文件，用于验证Dropbox功能是否正常工作。\n创建时间: " + str(dbx.users_get_current_account().email)
        test_file_path = "/sleep_data_test/test_file.txt"
        
        try:
            dbx.files_upload(
                test_content.encode('utf-8'),
                test_file_path,
                mode=dropbox.files.WriteMode.overwrite
            )
            print(f"✅ 成功上传测试文件: {test_file_path}")
        except Exception as e:
            print(f"⚠️  上传测试文件失败: {e}")
        
        print(f"\n🎉 所有测试通过! 新的Dropbox token工作正常!")
        return True
        
    except dropbox.exceptions.AuthError as e:
        print(f"❌ 认证错误: {e}")
        print("Token可能无效或已过期")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_updated_token()
    sys.exit(0 if success else 1) 