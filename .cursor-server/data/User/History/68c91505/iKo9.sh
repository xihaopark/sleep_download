#!/bin/bash
# PhysioNet Sleep Data Manager - 一键启动脚本
# 适用于已配置好的服务器

set -e

echo "======================================================================="
echo "🚀 PhysioNet Sleep Data Manager - 一键启动"
echo "======================================================================="

# 检查必要文件
echo "📋 检查必要文件..."
REQUIRED_FILES=("sleep_data_manager.py" "auto_upload_manager.py" "dropbox_config.py" "list.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少文件: $file"
        exit 1
    fi
done
echo "✅ 所有必要文件存在"

# 检查Python依赖
echo "📦 检查Python依赖..."
python3 -c "import requests, dropbox, time, os, sys" 2>/dev/null || {
    echo "❌ 缺少Python依赖，正在安装..."
    pip3 install requests dropbox
}
echo "✅ Python依赖检查完成"

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p download logs
echo "✅ 目录创建完成"

# 停止可能存在的旧进程
echo "🛑 停止旧进程..."
pkill -f sleep_data_manager || true
pkill -f auto_upload_manager || true
sleep 2

# 启动多进程系统
echo "🚀 启动多进程系统..."

# 启动wget版本管理器
echo "启动Wget下载上传管理器..."
nohup python3 sleep_data_wget_manager.py > logs/wget_manager.log 2>&1 &
MAIN_PID=$!

# 等待进程启动
sleep 3

# 验证进程状态
echo "✅ 验证进程状态..."
if ps -p $MAIN_PID > /dev/null; then
    echo "✅ Wget管理器运行中 (PID: $MAIN_PID)"
else
    echo "❌ Wget管理器启动失败"
fi

# 显示状态信息
echo ""
echo "======================================================================="
echo "🎉 启动完成！"
echo "======================================================================="
echo ""
echo "📊 当前状态:"
echo "- Wget管理器: PID $MAIN_PID"
echo "- 下载目录: $(ls -1 download 2>/dev/null | wc -l) 个文件"
echo "- 磁盘使用: $(df -h . | tail -1 | awk '{print $5}')"
echo "- 待下载: $(wc -l < list.txt) 个链接"
echo ""
echo "🛠️  管理命令:"
echo "  ./manage.sh status   # 查看状态"
echo "  ./manage.sh stop     # 停止所有进程"
echo "  ./manage.sh restart  # 重启所有进程"
echo "  ./manage.sh logs     # 查看日志"
echo ""
echo "📁 重要文件:"
echo "  list.txt                    # 下载链接列表"
echo "  uploaded_files.txt          # 已上传文件记录"
echo "  download_success.txt        # 下载成功记录"
echo "  logs/download_manager.log   # 下载日志"
echo "  logs/upload_manager.log     # 上传日志"
echo ""
echo "🔄 系统将自动:"
echo "  - 从list.txt下载文件"
echo "  - 检查文件完整性"
echo "  - 上传到Dropbox"
echo "  - 删除本地文件释放空间"
echo "  - 避免重复下载"
echo "=======================================================================" 