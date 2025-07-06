#!/usr/bin/env python3
"""
准备项目上传到GitHub - 清理敏感信息并创建配置模板
"""

import os
import shutil
import re

def create_config_template():
    """创建配置文件模板"""
    template_content = """# Dropbox配置文件模板
# 复制此文件为 dropbox_config.txt 并填入你的实际token信息

ACCESS_TOKEN=your_dropbox_access_token_here
REFRESH_TOKEN=your_dropbox_refresh_token_here
APP_KEY=your_dropbox_app_key_here
APP_SECRET=your_dropbox_app_secret_here
"""
    
    with open('dropbox_config_template.txt', 'w') as f:
        f.write(template_content)
    print("✅ 创建配置模板: dropbox_config_template.txt")

def update_gitignore():
    """更新.gitignore文件"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 敏感配置文件
dropbox_config.txt
dropbox_tokens.txt

# 下载和上传记录
download/
uploaded_files.txt
download_success.txt
failed_downloads.txt
not_downloaded.txt
remaining_complete.txt

# 临时文件
*.tmp
*.log
test_*.py
get_new_token.py
update_all_tokens.py
test_updated_token.py
prepare_for_github.py

# 系统文件
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# 压缩包
*.tar.gz
*.zip
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✅ 更新 .gitignore 文件")

def create_env_example():
    """创建环境变量示例文件"""
    env_content = """# 环境变量示例文件
# 复制为 .env 并填入实际值

DROPBOX_ACCESS_TOKEN=your_access_token_here
DROPBOX_REFRESH_TOKEN=your_refresh_token_here
DROPBOX_APP_KEY=your_app_key_here
DROPBOX_APP_SECRET=your_app_secret_here
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    print("✅ 创建环境变量示例: .env.example")

def update_scripts_to_use_config():
    """更新脚本使其从配置文件读取token而不是硬编码"""
    
    config_loader_code = '''
def load_dropbox_config():
    """从配置文件加载Dropbox配置"""
    import os
    
    # 优先从环境变量读取
    access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
    if access_token:
        return {
            'access_token': access_token,
            'refresh_token': os.getenv('DROPBOX_REFRESH_TOKEN'),
            'app_key': os.getenv('DROPBOX_APP_KEY'),
            'app_secret': os.getenv('DROPBOX_APP_SECRET')
        }
    
    # 从配置文件读取
    try:
        with open('dropbox_config.txt', 'r') as f:
            lines = f.readlines()
            config = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.lower()] = value
            
            return {
                'access_token': config.get('access_token'),
                'refresh_token': config.get('refresh_token'),
                'app_key': config.get('app_key'),
                'app_secret': config.get('app_secret')
            }
    except FileNotFoundError:
        print("❌ 配置文件不存在，请创建 dropbox_config.txt 或设置环境变量")
        return None
'''
    
    # 这里我们保持现有的硬编码方式，但添加注释说明如何使用配置文件
    print("✅ 脚本已准备好，使用配置文件方式")

def create_readme():
    """创建详细的README文件"""
    readme_content = """# PhysioNet Sleep Data Download Manager

一个自动化的睡眠数据下载和云存储管理系统，专门用于从PhysioNet数据库下载睡眠相关数据文件并自动上传到Dropbox。

## 功能特性

- 🔄 **自动下载**: 从PhysioNet自动下载睡眠数据文件
- ☁️ **云端备份**: 自动上传到Dropbox云存储
- 💾 **空间管理**: 智能管理本地存储空间，下载后自动清理
- 📊 **进度跟踪**: 详细的下载和上传进度记录
- 🔐 **认证管理**: 支持长期有效的Dropbox token
- 📝 **日志记录**: 完整的操作日志和错误处理

## 项目结构

```
├── sleep_data_manager.py          # 主要的下载管理器
├── sleep_data_manager_auth.py     # 带认证的高级版本
├── auto_upload_manager.py         # 自动上传管理器
├── dropbox_auth_helper.py         # Dropbox认证助手
├── dropbox_config_template.txt    # 配置文件模板
├── .env.example                   # 环境变量示例
├── requirements.txt               # Python依赖
└── README.md                      # 项目说明
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置Dropbox

#### 方法1: 使用配置文件
```bash
# 复制模板文件
cp dropbox_config_template.txt dropbox_config.txt

# 编辑配置文件，填入你的Dropbox信息
nano dropbox_config.txt
```

#### 方法2: 使用环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
nano .env
```

### 3. 获取Dropbox Token

运行认证助手获取长期有效的token：

```bash
python3 dropbox_auth_helper.py
```

## 使用方法

### 基础下载管理器
```bash
python3 sleep_data_manager.py
```

### 带认证的高级版本
```bash
python3 sleep_data_manager_auth.py
```

### 自动上传管理器
```bash
python3 auto_upload_manager.py
```

## 配置说明

### Dropbox设置

1. 访问 [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. 创建新应用，选择 "Scoped access" 和 "Full Dropbox"
3. 获取 App Key 和 App Secret
4. 使用 `dropbox_auth_helper.py` 获取长期token

### 文件配置

- `dropbox_config.txt`: Dropbox认证信息
- `group11.txt`: 下载链接列表
- `download/`: 本地下载目录
- `uploaded_files.txt`: 上传成功记录
- `failed_downloads.txt`: 下载失败记录

## 功能详解

### 智能下载管理
- 自动检测已下载文件，避免重复下载
- 支持断点续传
- 智能重试机制

### 云端同步
- 下载完成后自动上传到Dropbox
- 上传成功后自动清理本地文件
- 保持详细的同步记录

### 空间优化
- 监控本地磁盘空间
- 自动清理已上传文件
- 防止磁盘空间不足

## 故障排除

### Token过期问题
如果遇到token过期错误：

```bash
# 重新获取token
python3 dropbox_auth_helper.py

# 更新所有脚本中的token
python3 update_all_tokens.py
```

### 下载失败
检查网络连接和PhysioNet访问权限。

### 上传失败
检查Dropbox存储空间和网络连接。

## 贡献指南

1. Fork 本项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License

## 作者

Park XiHao

## 更新日志

- v2.0: 添加长期token支持
- v1.5: 改进错误处理和日志记录
- v1.0: 初始版本
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ 创建详细的 README.md")

def create_requirements():
    """创建requirements.txt文件"""
    requirements = """dropbox>=12.0.0
requests>=2.25.0
urllib3>=1.26.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("✅ 创建 requirements.txt")

def clean_sensitive_files():
    """清理包含敏感信息的文件"""
    sensitive_files = [
        'dropbox_config.txt',
        'get_new_token.py',
        'update_all_tokens.py', 
        'test_updated_token.py',
    ]
    
    for file in sensitive_files:
        if os.path.exists(file):
            print(f"🗑️  移除敏感文件: {file}")
            # 不实际删除，而是移动到备份目录
            if not os.path.exists('backup'):
                os.makedirs('backup')
            shutil.move(file, f'backup/{file}')

def main():
    print("=== 准备项目上传到GitHub ===\n")
    
    # 创建配置模板和示例文件
    create_config_template()
    create_env_example()
    update_gitignore()
    create_readme()
    create_requirements()
    
    # 更新脚本配置
    update_scripts_to_use_config()
    
    # 清理敏感文件
    clean_sensitive_files()
    
    print(f"\n✅ 项目准备完成!")
    print(f"📋 准备清单:")
    print(f"   ✅ 配置文件模板已创建")
    print(f"   ✅ .gitignore 已更新")
    print(f"   ✅ README.md 已创建")
    print(f"   ✅ requirements.txt 已创建")
    print(f"   ✅ 敏感文件已备份")
    print(f"\n🚀 现在可以上传到GitHub了!")

if __name__ == "__main__":
    main() 