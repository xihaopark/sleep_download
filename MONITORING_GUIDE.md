# 📊 项目进展实时监控指南

## 🎯 监控方法总览

### 1. 快速状态查看 ⚡
```bash
./manage.sh status
```
**适用场景**: 快速了解系统状态和最新活动

### 2. 简洁进度查看 📊
```bash
./quick_progress.sh
```
**适用场景**: 查看下载/上传进度条和基本统计

### 3. 实时进度监控 🔄
```bash
./progress_monitor.sh
```
**适用场景**: 持续监控，每10秒自动更新，包含详细统计和进度条

### 4. 传统监控方式 📋
```bash
./manage.sh monitor    # 实时监控模式
./manage.sh logs       # 查看详细日志
```

## 📈 监控信息说明

### 核心指标
- **总文件数**: `list.txt` 中的链接总数
- **已下载**: 成功下载的文件数量
- **已上传**: 成功上传到Dropbox的文件数量
- **本地缓存**: `download/` 目录中的文件数量
- **待处理**: 还未下载的文件数量

### 进度计算
- **下载进度** = 已下载 / 总文件数 × 100%
- **上传进度** = 已上传 / 总文件数 × 100%

### 系统状态
- **下载管理器**: 负责从PhysioNet下载文件
- **上传管理器**: 负责上传文件到Dropbox
- **磁盘使用**: 监控存储空间使用情况

## 🔍 实时日志查看

### 下载日志
```bash
tail -f logs/download_manager.log
```

### 上传日志
```bash
tail -f logs/upload_manager.log
```

### 查看最新活动
```bash
tail -10 logs/download_manager.log
tail -10 logs/upload_manager.log
```

## 📊 详细统计命令

### 基本统计
```bash
echo "总链接: $(wc -l < list.txt)"
echo "已下载: $(wc -l < download_success.txt 2>/dev/null || echo 0)"
echo "已上传: $(wc -l < uploaded_files.txt 2>/dev/null || echo 0)"
echo "本地文件: $(ls -1 download 2>/dev/null | wc -l)"
```

### 进度百分比
```bash
TOTAL=$(wc -l < list.txt)
DOWNLOADED=$(wc -l < download_success.txt 2>/dev/null || echo 0)
echo "下载进度: $((DOWNLOADED * 100 / TOTAL))%"
```

### 磁盘使用情况
```bash
df -h .
```

## 🚨 异常监控

### 检查进程状态
```bash
ps aux | grep -E "(sleep_data_manager|auto_upload_manager)" | grep -v grep
```

### 检查错误日志
```bash
grep -i error logs/*.log
grep -i failed logs/*.log
```

### 检查磁盘空间
```bash
df -h . | tail -1 | awk '{print $5}' | sed 's/%//' | awk '{if($1>90) print "警告: 磁盘使用率过高 "$1"%"}'
```

## 📱 监控最佳实践

### 日常监控
1. **每小时检查**: `./quick_progress.sh`
2. **发现异常时**: `./manage.sh status`
3. **详细分析**: `./manage.sh logs`

### 长期监控
1. **启动实时监控**: `./progress_monitor.sh`
2. **后台运行**: `nohup ./progress_monitor.sh > monitor.log 2>&1 &`

### 问题排查
1. **检查进程**: `./manage.sh status`
2. **查看日志**: `tail -50 logs/download_manager.log`
3. **重启系统**: `./manage.sh restart`

## 🎯 关键监控点

### 正常运行指标
- ✅ 下载管理器进程运行中
- ✅ 下载进度持续增长
- ✅ 磁盘使用率 < 90%
- ✅ 本地缓存文件数量合理

### 异常警告信号
- ❌ 进程意外停止
- ❌ 长时间无下载活动
- ❌ 磁盘空间不足
- ❌ 大量403错误（需要认证）

## 📋 监控脚本对比

| 脚本 | 更新频率 | 详细程度 | 适用场景 |
|------|----------|----------|----------|
| `quick_progress.sh` | 手动 | 中等 | 快速检查 |
| `progress_monitor.sh` | 10秒 | 详细 | 持续监控 |
| `manage.sh status` | 手动 | 简洁 | 状态概览 |
| `manage.sh monitor` | 10秒 | 中等 | 传统监控 |

---

**推荐**: 日常使用 `./quick_progress.sh`，长期监控使用 `./progress_monitor.sh` 