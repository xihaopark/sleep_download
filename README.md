# PhysioNet Sleep Data Download Manager

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
