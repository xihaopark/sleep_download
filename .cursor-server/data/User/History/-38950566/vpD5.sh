#!/bin/bash
# PhysioNet Sleep Data Manager - 一键部署脚本
# 适用于已有list.txt和部分数据的服务器

set -e  # 遇到错误立即退出

echo "======================================================================="
echo "🚀 PhysioNet Sleep Data Manager - 一键部署"
echo "   适用于已有数据的服务器快速部署"
echo "   密码: 1871"
echo "======================================================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 1. 克隆项目
echo "📦 步骤1: 克隆项目..."
if [ ! -d "sleep_download" ]; then
    git clone https://github.com/xihaopark/sleep_download.git
    echo "✅ 项目克隆完成"
else
    echo "✅ 项目已存在，更新中..."
    cd sleep_download && git pull && cd ..
fi

cd sleep_download

# 2. 安装依赖
echo "📦 步骤2: 安装Python依赖..."
pip3 install -r requirements.txt
echo "✅ 依赖安装完成"

# 3. 解密配置
echo "🔐 步骤3: 解密Dropbox配置..."
echo "1871" | python3 decrypt_sensitive.py
if [ $? -eq 0 ]; then
    echo "✅ 配置解密成功"
else
    echo "❌ 配置解密失败，请手动运行: python3 decrypt_sensitive.py"
    exit 1
fi

# 4. 备份现有数据
echo "💾 步骤4: 备份现有数据..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 备份现有的list.txt和状态文件
if [ -f "../list.txt" ]; then
    cp ../list.txt $BACKUP_DIR/
    echo "✅ 备份了现有的list.txt"
fi

if [ -f "../uploaded_files.txt" ]; then
    cp ../uploaded_files.txt $BACKUP_DIR/
    echo "✅ 备份了上传记录"
fi

if [ -f "../download_success.txt" ]; then
    cp ../download_success.txt $BACKUP_DIR/
    echo "✅ 备份了下载记录"
fi

if [ -d "../download" ]; then
    echo "📁 发现现有下载目录，文件数: $(ls -1 ../download | wc -l)"
    # 不移动download目录，保持原位置
fi

# 5. 合并配置
echo "🔧 步骤5: 合并现有配置..."

# 使用现有的list.txt（如果存在）
if [ -f "../list.txt" ]; then
    cp ../list.txt .
    echo "✅ 使用现有的list.txt ($(wc -l < list.txt) 行)"
else
    echo "⚠️  未找到现有的list.txt，请手动创建"
fi

# 合并上传记录
if [ -f "../uploaded_files.txt" ]; then
    if [ -f "uploaded_files.txt" ]; then
        cat ../uploaded_files.txt uploaded_files.txt | sort | uniq > temp_uploaded.txt
        mv temp_uploaded.txt uploaded_files.txt
    else
        cp ../uploaded_files.txt .
    fi
    echo "✅ 合并了上传记录"
fi

# 合并下载记录
if [ -f "../download_success.txt" ]; then
    if [ -f "download_success.txt" ]; then
        cat ../download_success.txt download_success.txt | sort | uniq > temp_success.txt
        mv temp_success.txt download_success.txt
    else
        cp ../download_success.txt .
    fi
    echo "✅ 合并了下载记录"
fi

# 6. 创建软链接到现有下载目录
echo "🔗 步骤6: 配置下载目录..."
if [ -d "../download" ]; then
    if [ -d "download" ]; then
        rm -rf download
    fi
    ln -s ../download download
    echo "✅ 链接到现有下载目录: $(ls -1 download | wc -l) 个文件"
else
    mkdir -p download
    echo "✅ 创建新的下载目录"
fi

# 7. 启动多进程系统
echo "🚀 步骤7: 启动多进程下载系统..."

# 停止可能存在的旧进程
pkill -f sleep_data_manager || true
pkill -f auto_upload_manager || true

# 启动多个进程
echo "启动基础下载管理器..."
nohup python3 sleep_data_manager.py > download_manager.log 2>&1 &
DOWNLOAD_PID=$!

echo "启动自动上传管理器..."
nohup python3 auto_upload_manager.py > upload_manager.log 2>&1 &
UPLOAD_PID=$!

echo "启动认证版管理器..."
nohup python3 sleep_data_manager_auth.py > auth_manager.log 2>&1 &
AUTH_PID=$!

# 等待一下让进程启动
sleep 3

# 8. 验证部署
echo "✅ 步骤8: 验证部署状态..."
echo "进程状态:"
ps aux | grep -E "(sleep_data|auto_upload)" | grep -v grep || echo "进程启动中..."

echo ""
echo "文件状态:"
echo "- 下载目录: $(ls -1 download 2>/dev/null | wc -l) 个文件"
echo "- 磁盘使用: $(df -h . | tail -1 | awk '{print $5}')"

# 9. 创建管理脚本
echo "🛠️  步骤9: 创建管理脚本..."
cat > manage.sh << 'EOF'
#!/bin/bash
# 管理脚本

case "$1" in
    status)
        echo "=== 进程状态 ==="
        ps aux | grep -E "(sleep_data|auto_upload)" | grep -v grep
        echo ""
        echo "=== 文件状态 ==="
        echo "下载目录: $(ls -1 download 2>/dev/null | wc -l) 个文件"
        echo "磁盘使用: $(df -h . | tail -1)"
        ;;
    stop)
        echo "停止所有进程..."
        pkill -f sleep_data_manager
        pkill -f auto_upload_manager
        echo "✅ 已停止"
        ;;
    start)
        echo "启动多进程系统..."
        nohup python3 sleep_data_manager.py > download_manager.log 2>&1 &
        nohup python3 auto_upload_manager.py > upload_manager.log 2>&1 &
        nohup python3 sleep_data_manager_auth.py > auth_manager.log 2>&1 &
        echo "✅ 已启动"
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    logs)
        echo "=== 下载日志 ==="
        tail -20 download_manager.log
        echo ""
        echo "=== 上传日志 ==="
        tail -20 upload_manager.log
        echo ""
        echo "=== 认证日志 ==="
        tail -20 auth_manager.log
        ;;
    *)
        echo "用法: $0 {status|start|stop|restart|logs}"
        ;;
esac
EOF

chmod +x manage.sh

echo ""
echo "======================================================================="
echo "🎉 部署完成！"
echo "======================================================================="
echo ""
echo "📊 当前状态:"
echo "- 项目目录: $(pwd)"
echo "- 备份目录: $BACKUP_DIR"
echo "- 下载进程: PID $DOWNLOAD_PID"
echo "- 上传进程: PID $UPLOAD_PID"
echo "- 认证进程: PID $AUTH_PID"
echo ""
echo "🛠️  管理命令:"
echo "  ./manage.sh status   # 查看状态"
echo "  ./manage.sh stop     # 停止所有进程"
echo "  ./manage.sh start    # 启动所有进程"
echo "  ./manage.sh restart  # 重启所有进程"
echo "  ./manage.sh logs     # 查看日志"
echo ""
echo "📁 重要文件:"
echo "  list.txt            # 下载链接列表"
echo "  uploaded_files.txt  # 已上传文件记录"
echo "  download/           # 下载目录"
echo "  dropbox_config.txt  # Dropbox配置(已解密)"
echo ""
echo "🔐 安全提醒: 部署完成后可删除dropbox_config.txt或重新加密"
echo "=======================================================================" 