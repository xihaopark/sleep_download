# 🚀 两步部署 PhysioNet Sleep Data Manager

## 第一步：克隆和配置

```bash
# 克隆项目
git clone https://github.com/xihaopark/sleep_download.git
cd sleep_download

# 配置敏感信息
cp sensitive_config_template.py dropbox_config.py
```

## 第二步：一键启动

```bash
# 一键启动
./quick_start.sh
```

## 🎉 完成！

系统将自动：
- ✅ 检查和安装依赖
- ✅ 创建必要目录
- ✅ 启动多进程下载和上传
- ✅ 智能合并现有数据
- ✅ 避免重复下载
- ✅ 自动空间管理

## 📊 管理命令

```bash
./manage.sh status    # 查看状态
./manage.sh monitor   # 实时监控
./manage.sh logs      # 查看日志
./manage.sh restart   # 重启系统
```

## 🔧 敏感信息配置

在 `dropbox_config.py` 中，所有必要信息已经预填：

```python
DROPBOX_CONFIG = {
    'access_token': 'sl.u.AF34PeTlpglqeAYwABIYfeD3-SyW3tTUqkcjG_o5ffO0YJ9nT_G2pd1wHYFRqqv7z0-LFZ6jg6soFpe3KCUNDqulVlMPIWG-Mf80Jvbw72x6S9NJV-5-0IbRlbmGGF8c0B3qXaU',
    'app_key': 'bl4dllhus4upqu9',
    'app_secret': '54ppgfj4c2hagos',
    'upload_folder': '/sleep_data'
}
```

## 🛡️ 系统特性

- **智能合并**: 自动识别和合并现有的 `list.txt` 和下载记录
- **避免重复**: 不会重复下载已有文件
- **空间优化**: 下载→验证→上传→删除，自动释放空间
- **多进程**: 并发下载和上传，提高效率
- **完整日志**: 详细记录所有操作，便于监控和调试
- **异常恢复**: 自动重试和错误处理

---

**就这么简单！两个命令搞定一切！** 🎯 