# Sleep Data Download Manager

🚀 **自动化PhysioNet睡眠数据下载和管理系统**

## 📋 项目概述

这是一个专为PhysioNet睡眠数据集设计的自动化下载和管理系统，支持：

- 🔐 **认证下载**：内置PhysioNet认证信息
- 📤 **自动上传**：下载完成后自动上传到Dropbox
- 🔄 **断点续传**：支持网络中断后继续下载
- 💾 **空间管理**：自动监控磁盘空间，上传后删除本地文件
- 🧵 **并行处理**：多线程下载和上传
- 📊 **状态监控**：实时显示进度和统计信息

## 🎯 主要特性

### 智能文件格式支持
- ✅ 完整URL：`https://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/filename.edf`
- ✅ 文件名：`filename.edf`（自动添加基础URL）
- ✅ 混合格式在同一文件中

### 多服务器部署
- 🖥️ 支持多台服务器并行处理不同数据集
- 📁 每台服务器处理不同的 `list*.txt` 文件
- 🔄 自动去重，避免重复下载

## 🚀 快速开始

### 1. 准备工作

```bash
# 创建下载目录
mkdir -p download/

# 将你的列表文件放入download目录
# 文件名格式：list*.txt (例如：list1.txt, list2.txt)
```

### 2. 列表文件格式

你的 `list*.txt` 文件可以包含：

```
# 注释行（以#开头会被忽略）
https://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/16474_18655.edf
16474_18655.tsv
16474_18655.atr
https://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/16477_1246.edf
16477_1246.tsv
16477_1246.atr
```

### 3. 运行程序

```bash
# 使用主程序（推荐）
python3 sleep_data_manager_auth.py

# 或使用自动部署脚本
chmod +x deploy.sh
./deploy.sh
```

## 📁 文件说明

### 核心程序文件
- `sleep_data_manager_auth.py` - 主程序，包含完整认证信息
- `sleep_data_manager.py` - 基础版本程序
- `auto_upload_manager.py` - 纯上传管理器

### 文档文件
- `README.md` - 项目主说明文件
- `PROJECT_README.md` - 技术详细文档
- `PROJECT_INTRODUCTION.md` - 用户友好指南
- `UPDATE_NOTICE.md` - 版本更新说明

### 部署文件
- `deploy.sh` - 自动部署脚本
- `.gitignore` - Git忽略文件配置

## 🔧 技术规格

### 系统要求
- Python 3.6+
- Linux/Unix系统
- 网络连接

### 依赖库
```bash
pip3 install requests
```

### 配置参数
- **下载线程**：2个并行线程
- **上传线程**：1个线程
- **块大小**：100MB（Dropbox分块上传）
- **超时设置**：300秒
- **重试次数**：3次（指数退避）

## 📊 功能特性

### 下载功能
- ✅ HTTP Basic认证
- ✅ 断点续传支持
- ✅ 文件完整性验证
- ✅ 自动重试机制
- ✅ 磁盘空间监控

### 上传功能
- ✅ Dropbox分块上传
- ✅ 大文件支持（>150MB）
- ✅ 上传后自动删除本地文件
- ✅ 上传状态记录

### 状态管理
- ✅ 已下载文件跟踪
- ✅ 已上传文件记录
- ✅ 失败任务日志
- ✅ 实时进度显示

## 🚀 多服务器部署

### 部署步骤
1. 将 `sleep_data_manager_auth.py` 复制到目标服务器
2. 在每台服务器上创建 `download/` 目录
3. 将对应的 `list*.txt` 文件放入各自的 `download/` 目录
4. 运行 `python3 sleep_data_manager_auth.py`

### 示例部署
```bash
# 服务器1 - 处理list1.txt
mkdir -p download/
cp list1.txt download/
python3 sleep_data_manager_auth.py

# 服务器2 - 处理list2.txt  
mkdir -p download/
cp list2.txt download/
python3 sleep_data_manager_auth.py
```

## 📈 监控和日志

程序运行时会显示：
```
📊 状态报告 [15:30:45]:
   下载: 25 个文件 (1250MB)
   上传: 20 个文件 (1000MB)
   跳过: 5 个文件
   失败: 0 个文件
   磁盘: 75.2% 使用 (12.5GB 可用)
   队列: 下载 50, 上传 3
```

## 🔒 安全说明

- 认证信息已内置在程序中
- Dropbox访问令牌已配置
- 所有网络请求使用HTTPS
- 本地文件在上传后自动删除

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

MIT License

## 📞 联系方式

如有问题，请通过GitHub Issues联系。

---

**⚡ 一键部署，自动化处理，让数据下载变得简单！** 