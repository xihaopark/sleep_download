# PhysioNet Sleep Data Manager - 通用部署指南

## 🌍 适用于任何环境的快速部署

无论你的项目文件结构如何，只要有下载链接列表，都可以快速部署这个自动化下载系统。

---

## 🚀 快速开始 (5分钟部署)

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

### 4. 准备你的下载链接
```bash
# 方式A: 如果你有自己的 list.txt 文件
cp /path/to/your/list.txt ./group11.txt

# 方式B: 如果链接在其他文件中
cp your_links_file.txt ./group11.txt

# 方式C: 手动创建
nano group11.txt
```

### 5. 启动系统
```bash
# 推荐: 带自动上传的版本
python3 sleep_data_manager_auth.py &

# 或者: 仅下载版本
python3 sleep_data_manager.py &
```

---

## 📁 适配不同文件结构

### 情况1: 你有现成的下载链接文件
```bash
# 假设你的链接文件叫 download_urls.txt
cp download_urls.txt group11.txt

# 或者直接修改脚本指向你的文件
sed -i 's/group11.txt/your_file_name.txt/g' sleep_data_manager_auth.py
```

### 情况2: 链接在数据库或其他格式
```bash
# 创建转换脚本
cat > convert_links.py << 'EOF'
#!/usr/bin/env python3
# 根据你的数据源调整这个脚本

# 示例: 从CSV转换
import csv
with open('your_data.csv', 'r') as f:
    reader = csv.reader(f)
    with open('group11.txt', 'w') as out:
        for row in reader:
            if 'physionet.org' in row[0]:  # 假设URL在第一列
                out.write(row[0] + '\n')

# 示例: 从JSON转换
import json
with open('your_data.json', 'r') as f:
    data = json.load(f)
    with open('group11.txt', 'w') as out:
        for item in data:
            if 'url' in item:
                out.write(item['url'] + '\n')
EOF

python3 convert_links.py
```

### 情况3: 多个链接文件
```bash
# 合并多个文件
cat list1.txt list2.txt list3.txt > group11.txt

# 或者去重合并
cat *.txt | sort | uniq > group11.txt
```

---

## ⚙️ 环境适配配置

### Docker部署 (推荐用于隔离环境)
```bash
# 创建Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python3 decrypt_sensitive.py < echo "1871"

CMD ["python3", "sleep_data_manager_auth.py"]
EOF

# 构建和运行
docker build -t sleep-downloader .
docker run -d --name sleep-downloader sleep-downloader
```

### 虚拟环境部署
```bash
# 创建虚拟环境
python3 -m venv sleep_env
source sleep_env/bin/activate

# 安装依赖
pip install -r requirements.txt

# 解密并运行
python3 decrypt_sensitive.py  # 输入1871
python3 sleep_data_manager_auth.py &
```

### 系统服务部署 (后台持久运行)
```bash
# 创建systemd服务
sudo tee /etc/systemd/system/sleep-downloader.service << 'EOF'
[Unit]
Description=Sleep Data Downloader
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/sleep_download
ExecStart=/usr/bin/python3 sleep_data_manager_auth.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable sleep-downloader
sudo systemctl start sleep-downloader
```

---

## 🔧 自定义配置

### 修改下载目录
```bash
# 编辑脚本，修改下载路径
sed -i 's|download/|/your/custom/path/|g' sleep_data_manager_auth.py
```

### 调整并发数
```bash
# 修改线程数 (默认4个)
sed -i 's/max_workers=4/max_workers=8/g' sleep_data_manager_auth.py
```

### 自定义Dropbox文件夹
```bash
# 修改上传路径
sed -i 's|/sleep_data|/your_folder|g' sleep_data_manager_auth.py
```

---

## 📊 监控和管理

### 查看运行状态
```bash
# 检查进程
ps aux | grep sleep_data

# 查看实时日志
tail -f nohup.out

# 查看系统资源
htop
```

### 管理下载任务
```bash
# 暂停下载
pkill -STOP -f sleep_data_manager

# 恢复下载
pkill -CONT -f sleep_data_manager

# 完全停止
pkill -f sleep_data_manager
```

### 备份和恢复
```bash
# 备份重要文件
tar -czf backup_$(date +%Y%m%d).tar.gz \
    uploaded_files.txt \
    download_success.txt \
    failed_downloads.txt \
    encrypted_config.json

# 恢复时解压
tar -xzf backup_YYYYMMDD.tar.gz
```

---

## 🔍 故障排除

### 常见问题

**1. Token过期**
```bash
# 重新获取token
python3 dropbox_auth_helper.py
python3 encrypt_sensitive.py  # 重新加密
```

**2. 磁盘空间不足**
```bash
# 清理已上传文件
python3 -c "
import os
with open('uploaded_files.txt', 'r') as f:
    for line in f:
        file_path = 'download/' + line.strip()
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f'Deleted: {file_path}')
"
```

**3. 网络连接问题**
```bash
# 测试连接
curl -I https://physionet.org
curl -I https://api.dropboxapi.com

# 重启网络服务
sudo systemctl restart networking
```

**4. 权限问题**
```bash
# 修复权限
chmod +x *.py
chown -R $USER:$USER .
```

---

## 🎯 性能优化建议

### 针对不同服务器配置

**低配置服务器 (1核2GB)**
```bash
# 减少并发数
sed -i 's/max_workers=4/max_workers=2/g' sleep_data_manager_auth.py
```

**高配置服务器 (4核8GB+)**
```bash
# 增加并发数
sed -i 's/max_workers=4/max_workers=8/g' sleep_data_manager_auth.py
```

**网络带宽限制**
```bash
# 添加下载限速 (需要修改脚本)
# 在requests.get()中添加: stream=True, timeout=30
```

---

## 📞 快速支持

### 一键诊断脚本
```bash
cat > diagnose.py << 'EOF'
#!/usr/bin/env python3
import os, sys, subprocess

print("=== Sleep Data Manager 诊断 ===")
print(f"Python版本: {sys.version}")
print(f"工作目录: {os.getcwd()}")

# 检查文件
files = ['group11.txt', 'encrypted_config.json', 'decrypt_sensitive.py']
for f in files:
    status = "✅" if os.path.exists(f) else "❌"
    print(f"{status} {f}")

# 检查进程
try:
    result = subprocess.run(['pgrep', '-f', 'sleep_data'], capture_output=True, text=True)
    if result.stdout:
        print(f"✅ 进程运行中: PID {result.stdout.strip()}")
    else:
        print("❌ 进程未运行")
except:
    print("❌ 无法检查进程")

# 检查磁盘空间
try:
    result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
    print(f"💾 磁盘空间:\n{result.stdout}")
except:
    print("❌ 无法检查磁盘空间")
EOF

python3 diagnose.py
```

---

**🔑 记住密码: 1871**

**📧 需要帮助? 联系: xihaopark@gmail.com** 