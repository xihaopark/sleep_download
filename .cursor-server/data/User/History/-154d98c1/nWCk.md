# Sleep Data 自动化管理器

## 📋 项目概述

这是一个用于自动化下载和管理PhysioNet睡眠数据的Python程序。支持并行下载、自动上传到Dropbox、断点续传、磁盘空间管理等功能。

## 🚀 核心功能

- ✅ **并行下载**: 使用PhysioNet认证，支持断点续传
- ✅ **自动上传**: 分块上传大文件到Dropbox，上传后自动删除本地文件
- ✅ **状态管理**: 自动跟踪已下载、已上传文件，避免重复处理
- ✅ **磁盘监控**: 智能监控磁盘空间，防止空间不足
- ✅ **错误重试**: 自动重试失败的下载，记录错误日志

## 📁 文件结构

```
项目根目录/
├── sleep_data_manager_auth.py    # 主程序（必需）
├── download/                     # 下载目录
│   └── list*.txt                # 下载列表文件（必需）
├── uploaded_files.txt           # 已上传文件记录
├── download_success.txt         # 下载成功记录
├── failed_downloads.txt         # 失败下载记录
└── PROJECT_README.md           # 本说明文件
```

## 🔧 部署步骤

### 1. 复制核心文件
```bash
# 只需要复制这个主程序文件
scp sleep_data_manager_auth.py user@target-server:/root/
```

### 2. 准备下载列表
在目标服务器上创建 `download/` 目录，并放入相应的下载列表文件：
```bash
mkdir -p download/
# 将你的 group*.txt 文件放入 download/ 目录
```

### 3. 一键启动
```bash
python3 sleep_data_manager_auth.py
```

## ⚙️ 配置说明

程序内置了所有必要的配置，无需额外设置：

- **PhysioNet认证**: `chenzcha` / `97HU15lWcE`
- **Dropbox令牌**: 已内置有效令牌
- **并发设置**: 2个下载线程 + 1个上传线程
- **超时设置**: 300秒（对应wget --timeout=300）

## 📊 状态文件说明

| 文件名 | 用途 | 说明 |
|--------|------|------|
| `uploaded_files.txt` | 已上传记录 | 记录已成功上传到Dropbox的文件 |
| `download_success.txt` | 下载成功记录 | 记录已成功下载的文件 |
| `failed_downloads.txt` | 失败记录 | 记录下载失败的URL和错误信息 |

## 🔄 工作流程

1. **启动时**: 自动扫描现有文件，加载待处理任务
2. **下载阶段**: 并行下载文件，支持断点续传
3. **上传阶段**: 自动上传大文件到Dropbox
4. **清理阶段**: 上传成功后删除本地文件释放空间
5. **状态更新**: 实时更新各种状态文件

## 📈 监控信息

程序每60秒输出一次状态报告：
```
📊 状态报告 [15:30:45]:
   下载: 15 个文件 (2048MB)
   上传: 12 个文件 (1536MB)
   跳过: 25 个文件
   失败: 3 个文件
   磁盘: 75.2% 使用 (8.5GB 可用)
   队列: 下载 45, 上传 8
```

## 🛠️ 故障排除

### 下载失败
- 检查网络连接
- 确认PhysioNet认证信息正确
- 查看 `failed_downloads.txt` 了解具体错误

### 上传失败
- 检查Dropbox令牌是否有效
- 确认网络连接稳定
- 检查Dropbox存储空间

### 磁盘空间不足
- 程序会自动暂停下载当磁盘使用率超过90%
- 优先上传大文件释放空间
- 手动删除不需要的文件

## 🔄 重启和恢复

程序支持随时中断和重启：
- 按 `Ctrl+C` 安全退出
- 重新运行会从上次停止的地方继续
- 所有状态信息都会自动保存和恢复

## 📞 技术支持

如遇问题，请检查：
1. Python版本 >= 3.6
2. 必要的Python包: `requests`
3. 网络连接正常
4. 磁盘空间充足

---
*本项目由AI Assistant开发，专为PhysioNet睡眠数据批量处理设计* 