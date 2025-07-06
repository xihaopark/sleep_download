# 🎯 PhysioNet Sleep Data Manager - 系统概览

## 核心功能
**一句话总结**: 从 `list.txt` 批量下载文件，临时缓存后上传到Dropbox，然后删除本地文件释放空间。

## 数据流程
```
📋 list.txt → 📥 wget下载 → 💾 本地缓存 → ☁️ Dropbox上传 → 🗑️ 删除本地
```

## 关键组件

### 📍 部署位置
- **固定路径**: `/root/sleep_download/`
- **核心文件**: `list.txt` (下载链接列表)
- **缓存目录**: `download/` (临时存储)

### 🔑 认证信息
- **Dropbox Token**: 有时限，需要动态更新
- **PhysioNet密码**: 已预配置，用于认证下载
- **配置文件**: `dropbox_config.py` (从模板复制)

### 🔄 自动化流程
1. **读取列表**: 从 `list.txt` 读取URL
2. **并发下载**: 多线程下载到 `download/`
3. **实时上传**: 下载完成立即上传
4. **空间释放**: 上传成功后删除本地文件
5. **状态记录**: 记录成功/失败状态

## 两步部署

### 第一步：获取和配置
```bash
cd /root
git clone https://github.com/xihaopark/sleep_download.git
cd sleep_download
cp sensitive_config_template.py dropbox_config.py
```

### 第二步：启动
```bash
./quick_start.sh
```

## 管理命令
```bash
./manage.sh status    # 查看状态
./manage.sh monitor   # 实时监控  
./manage.sh restart   # 重启系统
./test_deployment.sh  # 部署测试
```

## 核心特性
- ✅ **智能跳过**: 不重复下载已有文件
- ✅ **空间管理**: 自动释放磁盘空间
- ✅ **错误重试**: 自动重试失败操作
- ✅ **实时监控**: 详细状态和日志
- ✅ **并发处理**: 多线程提高效率

---
**就这么简单**: 维护好 `list.txt` 文件，系统自动处理其余一切。 