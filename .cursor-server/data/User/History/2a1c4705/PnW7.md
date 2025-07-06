# PhysioNet Sleep Data Manager - Wget版

🚀 **高效的PhysioNet睡眠数据下载和Dropbox上传管理系统**

专为处理大规模睡眠数据集设计，使用wget进行稳定下载，自动上传到Dropbox，智能管理磁盘空间。

## ✨ 特性

- 🔗 **Wget下载**: 使用wget实现稳定可靠的下载
- ☁️ **Dropbox自动上传**: 下载完成后自动上传到云端
- 💾 **智能空间管理**: 自动监控磁盘空间，防止空间不足
- 🔄 **断点续传**: 支持下载中断后继续
- 🚫 **防重复下载**: 智能跳过已下载和已上传的文件
- 📊 **实时监控**: 显示下载上传进度和系统状态
- 🧵 **多线程处理**: 支持并发下载和上传
- 📝 **详细日志**: 完整的操作记录和错误追踪

## 🛠️ 安装部署

### 1. 系统要求

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip wget

# CentOS/RHEL
sudo yum install -y python3 python3-pip wget

# 或者使用dnf (较新版本)
sudo dnf install -y python3 python3-pip wget
```

### 2. 安装Python依赖

```bash
pip3 install requests pathlib
```

### 3. 下载项目

```bash
git clone https://github.com/yourusername/physionet-sleep-data-manager.git
cd physionet-sleep-data-manager
```

### 4. 配置系统

```bash
# 运行配置脚本
python3 setup_config.py
```

按提示输入：
- PhysioNet用户名和密码
- Dropbox访问令牌
- 下载和上传配置

### 5. 准备数据

将下载链接放入 `list.txt` 文件：
```
https://physionet.org/files/sleep-edf/1.0.0/sleep-cassette/SC4001E0-PSG.edf
https://physionet.org/files/sleep-edf/1.0.0/sleep-cassette/SC4001EC-Hypnogram.edf
...
```

## 🚀 快速开始

### 方法1: 一键启动

```bash
# 给脚本执行权限
chmod +x quick_start.sh

# 一键启动
./quick_start.sh
```

### 方法2: 手动启动

```bash
# 创建必要目录
mkdir -p download logs

# 启动管理器
python3 sleep_data_wget_manager.py
```

### 方法3: 后台运行

```bash
# 后台运行
nohup python3 sleep_data_wget_manager.py > logs/wget_manager.log 2>&1 &

# 查看日志
tail -f logs/wget_manager.log
```

## 🎛️ 管理命令

使用内置管理脚本：

```bash
# 给管理脚本执行权限
chmod +x manage.sh

# 查看系统状态
./manage.sh status

# 启动系统
./manage.sh start

# 停止系统
./manage.sh stop

# 重启系统
./manage.sh restart

# 查看详细日志
./manage.sh logs

# 清理系统文件
./manage.sh clean

# 实时监控
./manage.sh monitor
```

## 📊 监控和状态

### 实时状态查看

```bash
# 查看进程状态
ps aux | grep sleep_data_wget_manager

# 查看磁盘使用
df -h

# 查看文件数量
ls -la download/ | wc -l

# 查看下载进度
wc -l download_success.txt
wc -l uploaded_files.txt
```

### 日志文件

- `logs/wget_manager.log` - 主要日志
- `download_success.txt` - 下载成功记录
- `uploaded_files.txt` - 上传成功记录
- `failed_downloads.txt` - 失败记录

## ⚙️ 配置说明

### dropbox_config.py 配置文件

```python
# PhysioNet 配置
PHYSIONET_CONFIG = {
    'username': 'your_username',
    'password': 'your_password'
}

# Dropbox 配置
DROPBOX_CONFIG = {
    'access_token': 'your_access_token',
    'upload_folder': '/Sleep_Data'
}

# 下载配置
DOWNLOAD_CONFIG = {
    'max_concurrent_downloads': 3,    # 并发下载数
    'retry_attempts': 3,              # 重试次数
    'download_timeout': 300,          # 下载超时(秒)
    'min_free_space_gb': 5           # 最小剩余空间(GB)
}

# 上传配置
UPLOAD_CONFIG = {
    'delete_after_upload': True,      # 上传后删除本地文件
    'upload_chunk_size': 8*1024*1024  # 上传块大小(8MB)
}
```

### 高级配置

```bash
# 修改wget参数
# 在 sleep_data_wget_manager.py 中的 download_with_wget 方法

# 修改并发数
# 在配置文件中调整 max_concurrent_downloads

# 修改磁盘空间阈值
# 在配置文件中调整 min_free_space_gb
```

## 🔧 故障排除

### 常见问题

1. **下载失败**
   ```bash
   # 检查网络连接
   wget --spider https://physionet.org
   
   # 检查认证信息
   wget --user=username --password=password https://physionet.org/files/...
   ```

2. **上传失败**
   ```bash
   # 检查Dropbox token
   python3 -c "
   import requests
   token = 'your_token'
   r = requests.post('https://api.dropboxapi.com/2/users/get_current_account',
                     headers={'Authorization': f'Bearer {token}'})
   print(r.status_code, r.text)
   "
   ```

3. **磁盘空间不足**
   ```bash
   # 清理下载目录
   find download -name "*.tmp" -delete
   
   # 手动上传并删除大文件
   python3 -c "
   from pathlib import Path
   for f in Path('download').glob('*.edf'):
       if f.stat().st_size > 100*1024*1024:  # >100MB
           print(f)
   "
   ```

### 性能优化

```bash
# 1. 调整并发数
# 编辑配置文件，根据网络和磁盘性能调整

# 2. 调整上传块大小
# 网络好的情况下可以增加到16MB或32MB

# 3. 使用SSD存储
# 将download目录移动到SSD

# 4. 监控系统资源
htop
iotop
```

## 📈 性能指标

- **下载速度**: 通常2-5MB/s（取决于网络）
- **上传速度**: 通常1-3MB/s（取决于网络）
- **并发处理**: 支持3-10个并发下载
- **内存使用**: 通常<100MB
- **磁盘I/O**: 优化的顺序读写

## 🔐 安全说明

- 配置文件包含敏感信息，请妥善保管
- 不要将配置文件提交到版本控制系统
- 定期更新Dropbox访问令牌
- 使用强密码保护PhysioNet账户

## 📞 支持

如遇问题，请查看：
1. 日志文件 `logs/wget_manager.log`
2. 系统状态 `./manage.sh status`
3. 磁盘空间 `df -h`

## 🤝 贡献

欢迎提交Issue和Pull Request！

## �� 许可证

MIT License
