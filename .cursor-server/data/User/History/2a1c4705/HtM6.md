# PhysioNet Sleep Data Manager

自动化PhysioNet睡眠数据下载、验证和Dropbox上传系统。

## 🚀 快速开始

### 1. 配置敏感信息
将 `sensitive_config_template.py` 复制为 `dropbox_config.py`：
```bash
cp sensitive_config_template.py dropbox_config.py
```

### 2. 准备下载列表
确保 `list.txt` 文件包含要下载的URL，每行一个：
```
https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf
https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf.sha256
...
```

### 3. 一键启动
```bash
chmod +x quick_start.sh
./quick_start.sh
```

## 🛠️ 管理命令

```bash
# 查看系统状态
./manage.sh status

# 启动系统
./manage.sh start

# 停止系统
./manage.sh stop

# 重启系统
./manage.sh restart

# 查看日志
./manage.sh logs

# 清理系统
./manage.sh clean

# 实时监控
./manage.sh monitor
```

## 📁 文件结构

```
.
├── sleep_data_manager.py      # 主下载管理器
├── auto_upload_manager.py     # 自动上传管理器
├── dropbox_config.py          # 配置文件 (需要自己创建)
├── list.txt                   # 下载链接列表
├── download/                  # 下载目录
├── logs/                      # 日志目录
├── quick_start.sh             # 一键启动脚本
├── manage.sh                  # 管理脚本
├── uploaded_files.txt         # 已上传文件记录
└── download_success.txt       # 下载成功记录
```

## 🔧 配置说明

### Dropbox配置
在 `dropbox_config.py` 中配置：
- `access_token`: Dropbox访问令牌
- `app_key`: Dropbox应用密钥
- `app_secret`: Dropbox应用密钥
- `upload_folder`: 上传目录路径

### 下载配置
- `max_concurrent_downloads`: 最大并发下载数
- `retry_attempts`: 重试次数
- `download_timeout`: 下载超时时间
- `min_free_space_gb`: 最小剩余空间

### 上传配置
- `upload_after_download`: 下载后立即上传
- `delete_after_upload`: 上传后删除本地文件
- `verify_upload`: 验证上传完整性

## 🔄 工作流程

1. **下载**: 从 `list.txt` 读取URL并下载到 `download/` 目录
2. **验证**: 检查文件完整性（SHA256校验）
3. **上传**: 自动上传到Dropbox指定目录
4. **清理**: 上传成功后删除本地文件释放空间
5. **记录**: 记录所有操作避免重复处理

## 📊 监控和日志

- **实时状态**: `./manage.sh status`
- **实时监控**: `./manage.sh monitor`
- **下载日志**: `logs/download_manager.log`
- **上传日志**: `logs/upload_manager.log`

## 🛡️ 安全特性

- 自动重试机制
- 文件完整性验证
- 磁盘空间监控
- 重复下载检测
- 进程异常恢复

## 🔧 故障排除

### 常见问题

1. **Token过期**
   - 更新 `dropbox_config.py` 中的 `access_token`

2. **磁盘空间不足**
   - 系统会自动暂停下载
   - 清理不需要的文件或增加磁盘空间

3. **网络连接问题**
   - 系统会自动重试
   - 检查网络连接和防火墙设置

4. **进程异常退出**
   - 使用 `./manage.sh restart` 重启系统
   - 检查日志文件了解详细错误信息

### 日志分析
```bash
# 查看错误日志
grep -i error logs/*.log

# 查看最新活动
tail -f logs/download_manager.log

# 统计下载进度
wc -l download_success.txt
```

## 📈 性能优化

- 根据网络带宽调整并发下载数
- 根据磁盘空间调整清理策略
- 根据Dropbox API限制调整上传频率

## 🆘 紧急操作

```bash
# 立即停止所有进程
./manage.sh stop

# 清理所有临时文件
./manage.sh clean

# 重新开始（保留记录）
./manage.sh restart
```
