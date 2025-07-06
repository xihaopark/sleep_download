# 📋 PhysioNet Sleep Data Manager - 部署须知

## 🎯 系统核心功能

这个系统就做一件事：**自动化数据流转**

```
list.txt → wget下载 → 本地缓存 → 上传Dropbox → 删除本地文件
```

### 📝 具体流程

1. **读取下载列表**: 从 `list.txt` 文件读取所有需要下载的URL
2. **批量下载**: 使用wget方式下载文件到本地 `download/` 目录
3. **临时缓存**: 下载的文件暂存在本地，等待上传
4. **上传到云端**: 自动上传到Dropbox云存储
5. **释放空间**: 上传成功后立即删除本地文件，释放磁盘空间

## 🏗️ 部署环境要求

### 📍 部署位置
- **固定路径**: `/root/` 目录下
- **项目目录**: `/root/sleep_download/`
- **不要更改路径**: 系统配置基于此路径

### 📁 目录结构
```
/root/
├── sleep_download/              # 项目根目录
│   ├── list.txt                 # 下载链接列表 (核心文件)
│   ├── download/                # 本地缓存目录
│   │   ├── *.edf               # 下载的EDF文件
│   │   ├── *.tsv               # 下载的TSV文件
│   │   └── *.atr               # 下载的ATR文件
│   ├── dropbox_config.py        # Dropbox配置 (需要创建)
│   ├── uploaded_files.txt       # 已上传文件记录
│   ├── download_success.txt     # 下载成功记录
│   └── logs/                    # 日志目录
```

## 🔑 认证和Token管理

### 📊 Dropbox Token问题
- **Token有时限**: Dropbox访问令牌会过期
- **自动更新**: 系统支持长期token和动态刷新
- **预配置**: 模板文件已包含有效token

### 🔐 PhysioNet认证
- **用户名/密码**: 部分文件需要PhysioNet账户认证
- **已知密码**: 系统已预配置认证信息
- **自动处理**: 下载时自动使用认证

## 🚀 一键部署步骤

### 第一步：获取项目
```bash
# 克隆到固定位置
cd /root
git clone https://github.com/xihaopark/sleep_download.git
cd sleep_download
```

### 第二步：配置敏感信息
```bash
# 复制配置模板 (已预填所有信息)
cp sensitive_config_template.py dropbox_config.py
```

### 第三步：启动系统
```bash
# 一键启动
./quick_start.sh
```

## 📋 关键文件说明

### 🎯 list.txt (核心文件)
```
# 下载链接列表，每行一个URL
https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf
https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf.sha256
https://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/655_9427.edf
...
```

### 🔧 dropbox_config.py (敏感信息)
```python
DROPBOX_CONFIG = {
    'access_token': 'sl.u.AF34PeTlpglqeAYwABIYfeD3-SyW3tTUqkcjG_o5ffO0YJ9nT_G2pd1wHYFRqqv7z0...',
    'app_key': 'bl4dllhus4upqu9',
    'app_secret': '54ppgfj4c2hagos',
    'upload_folder': '/sleep_data'
}
```

### 📁 download/ (本地缓存)
- **作用**: 临时存储下载的文件
- **自动清理**: 上传成功后自动删除
- **空间管理**: 避免磁盘空间不足

## 🔄 系统工作原理

### 📥 下载阶段
1. 读取 `list.txt` 中的URL
2. 跳过已下载的文件 (检查 `download_success.txt`)
3. 使用wget下载到 `download/` 目录
4. 验证文件完整性
5. 记录下载成功

### 📤 上传阶段
1. 扫描 `download/` 目录中的文件
2. 跳过已上传的文件 (检查 `uploaded_files.txt`)
3. 分块上传大文件到Dropbox
4. 验证上传成功
5. 删除本地文件释放空间
6. 记录上传成功

### 🔁 循环处理
- **并发处理**: 同时进行下载和上传
- **智能调度**: 大文件优先上传
- **错误重试**: 自动重试失败的操作
- **状态同步**: 实时更新处理状态

## 💾 空间管理策略

### 🎯 容量限制处理
- **监控磁盘**: 实时监控磁盘使用率
- **智能暂停**: 空间不足时暂停下载
- **优先上传**: 优先上传大文件释放空间
- **自动清理**: 上传成功立即删除本地文件

### 📊 存储优化
- **分块上传**: 大文件分块上传，减少内存占用
- **批量处理**: 批量上传多个文件
- **压缩日志**: 自动清理和压缩日志文件

## 🛠️ 管理和监控

### 📊 状态查看
```bash
./manage.sh status    # 查看系统状态
./manage.sh monitor   # 实时监控
./manage.sh logs      # 查看详细日志
```

### 🔧 系统控制
```bash
./manage.sh start     # 启动系统
./manage.sh stop      # 停止系统
./manage.sh restart   # 重启系统
./manage.sh clean     # 清理系统
```

### 📈 进度跟踪
- **实时统计**: 显示下载/上传进度
- **文件计数**: 统计处理的文件数量
- **空间使用**: 监控磁盘空间变化
- **错误记录**: 记录和分析失败原因

## ⚠️ 注意事项

### 🔒 安全要求
- **固定路径**: 必须在 `/root/` 下部署
- **权限管理**: 确保脚本有执行权限
- **配置保护**: 保护 `dropbox_config.py` 文件

### 📡 网络要求
- **稳定网络**: 需要稳定的网络连接
- **防火墙**: 确保可以访问PhysioNet和Dropbox
- **带宽充足**: 大文件传输需要足够带宽

### 💿 存储要求
- **磁盘空间**: 至少5GB可用空间
- **文件系统**: 支持大文件存储
- **读写权限**: 确保有足够的读写权限

## 🎉 部署验证

### 🧪 运行测试
```bash
# 运行完整部署测试
./test_deployment.sh
```

### ✅ 验证清单
- [ ] 项目在 `/root/sleep_download/` 目录
- [ ] `list.txt` 文件存在且有内容
- [ ] `dropbox_config.py` 配置正确
- [ ] 系统进程正常运行
- [ ] 日志文件正常写入
- [ ] 网络连接正常

---

**总结**: 这就是一个简单的数据流转系统，从本地列表下载文件，临时缓存后上传到云端，然后删除本地文件。核心是处理 `list.txt` 中的URL，管理本地 `download/` 目录的文件流转。 