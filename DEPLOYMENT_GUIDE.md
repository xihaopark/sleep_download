# PhysioNet Sleep Data Manager - 完整部署指南

## 🔐 敏感信息保护

**密码: 1871**

项目中的敏感信息已使用密码1871加密保护：
- `encrypted_config.json` - 加密的Dropbox配置
- `decrypt_sensitive.py` - 解密脚本

## 🚀 快速部署

### 1. 克隆项目
```bash
git clone https://github.com/xihaopark/sleep_download.git
cd sleep_download
```

### 2. 安装依赖
```bash
pip3 install -r requirements.txt
```

### 3. 解密配置 🔑
```bash
python3 decrypt_sensitive.py
# 输入密码: 1871
```

### 4. 启动系统
```bash
# 方式1: 基础下载管理器
python3 sleep_data_manager.py

# 方式2: 带自动上传的高级版本 (推荐)
python3 sleep_data_manager_auth.py

# 方式3: 后台运行
python3 sleep_data_manager_auth.py &
```

## 📋 项目文件说明

### 核心脚本
- `sleep_data_manager.py` - 基础下载管理器
- `sleep_data_manager_auth.py` - 高级版本(下载+上传+认证)
- `auto_upload_manager.py` - 独立上传管理器
- `dropbox_auth_helper.py` - Dropbox认证助手

### 配置文件
- `encrypted_config.json` - 🔐 加密的Dropbox配置
- `decrypt_sensitive.py` - 🔓 解密脚本 (密码: 1871)
- `dropbox_config_template.txt` - 配置模板
- `.env.example` - 环境变量示例

### 数据文件
- `not_downloaded.txt` - 待下载文件列表
- `group11.txt` - 下载链接文件
- `uploaded_files.txt` - 已上传文件记录
- `failed_downloads.txt` - 下载失败记录

## ⚙️ 系统功能

### 🔄 自动化流程
1. **并行下载** - 多线程下载PhysioNet睡眠数据
2. **自动上传** - 下载完成立即上传到Dropbox
3. **空间管理** - 上传后自动删除本地文件
4. **状态跟踪** - 详细的进度和错误记录
5. **断点续传** - 支持中断后继续下载

### 📊 监控功能
- 实时进度显示
- 磁盘空间监控
- 下载/上传速度统计
- 失败重试机制

## 🛠️ 高级配置

### Dropbox配置
解密后的`dropbox_config.txt`包含：
```
ACCESS_TOKEN=your_long_lived_token
REFRESH_TOKEN=your_refresh_token
APP_KEY=your_app_key
APP_SECRET=your_app_secret
```

### 环境变量方式
```bash
export DROPBOX_ACCESS_TOKEN="your_token"
export DROPBOX_REFRESH_TOKEN="your_refresh_token"
export DROPBOX_APP_KEY="your_app_key"
export DROPBOX_APP_SECRET="your_app_secret"
```

## 🔧 故障排除

### Token过期
如果遇到token过期：
```bash
python3 dropbox_auth_helper.py
# 重新获取长期token
```

### 重新加密配置
```bash
python3 encrypt_sensitive.py
# 使用密码1871重新加密
```

### 检查运行状态
```bash
# 查看后台进程
ps aux | grep sleep_data

# 查看实时日志
tail -f nohup.out

# 停止后台进程
pkill -f sleep_data_manager
```

## 📈 性能优化

### 推荐配置
- **CPU**: 2核以上
- **内存**: 4GB以上
- **存储**: 20GB可用空间
- **网络**: 稳定的互联网连接

### 并发设置
脚本默认4个工作线程，可根据服务器性能调整：
- 修改`max_workers=4`参数
- 建议不超过CPU核心数的2倍

## 🔒 安全注意事项

1. **密码保护** - 所有敏感信息已加密 (密码: 1871)
2. **Token管理** - 使用长期有效的refresh token
3. **访问控制** - 限制服务器访问权限
4. **定期备份** - 重要配置文件定期备份

## 📞 支持

- **GitHub**: https://github.com/xihaopark/sleep_download
- **作者**: Park XiHao
- **邮箱**: xihaopark@gmail.com

---

**重要提醒**: 部署完成后记得删除敏感信息或限制访问权限！🔐 