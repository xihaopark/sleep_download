#!/usr/bin/env python3
"""
更新所有脚本中的Dropbox token
"""

import os
import re

def load_new_token():
    """从配置文件加载新token"""
    try:
        with open('dropbox_config.txt', 'r') as f:
            lines = f.readlines()
            config = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
            return config.get('ACCESS_TOKEN')
    except FileNotFoundError:
        print("❌ 找不到 dropbox_config.txt 文件")
        return None

def update_token_in_file(file_path, new_token):
    """更新单个文件中的token"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配旧的token模式 (sl.u.开头的长字符串)
        old_token_pattern = r'sl\.u\.[A-Za-z0-9_-]+'
        
        # 检查是否包含旧token
        if re.search(old_token_pattern, content):
            print(f"🔄 更新文件: {file_path}")
            
            # 替换token
            updated_content = re.sub(old_token_pattern, new_token, content)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏭️  跳过: {file_path} (无需更新)")
            return False
            
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {e}")
        return False

def main():
    print("=== 更新所有脚本中的Dropbox Token ===\n")
    
    # 加载新token
    new_token = load_new_token()
    if not new_token:
        print("❌ 无法加载新token，请先运行 get_new_token.py")
        return
    
    print(f"新Token: {new_token[:50]}...")
    print()
    
    # 需要更新的Python文件列表
    python_files = [
        'sleep_data_manager.py',
        'sleep_data_manager_auth.py', 
        'auto_upload_manager.py',
    ]
    
    # 检查并更新每个文件
    updated_count = 0
    for file_path in python_files:
        if os.path.exists(file_path):
            if update_token_in_file(file_path, new_token):
                updated_count += 1
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    print(f"\n📊 更新统计:")
    print(f"- 总共检查文件: {len(python_files)}")
    print(f"- 成功更新文件: {updated_count}")
    
    if updated_count > 0:
        print(f"\n✅ Token更新完成! 已更新 {updated_count} 个文件")
        print("现在所有脚本都使用新的长期有效token了！")
    else:
        print(f"\n⚠️  没有文件需要更新")

if __name__ == "__main__":
    main() 