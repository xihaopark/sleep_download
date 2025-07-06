#!/bin/bash
# Sleep Data Manager 部署脚本

echo "🚀 Sleep Data Manager 部署脚本"
echo "================================"

# 检查Python环境
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

python3 -c "import requests" 2>/dev/null || {
    echo "📦 安装requests库..."
    pip3 install requests
}

# 创建必要目录
echo "📁 创建目录结构..."
mkdir -p download

# 检查主程序文件
if [ ! -f "sleep_data_manager_auth.py" ]; then
    echo "❌ 主程序文件 sleep_data_manager_auth.py 不存在"
    echo "请确保已复制该文件到当前目录"
    exit 1
fi

# 给主程序添加执行权限
chmod +x sleep_data_manager_auth.py

# 检查下载列表文件
echo "📋 检查下载列表文件..."
if ls download/group*.txt 1> /dev/null 2>&1; then
    echo "✅ 找到下载列表文件:"
    ls download/group*.txt
else
    echo "⚠️  未找到下载列表文件 (download/group*.txt)"
    echo "请将你的下载列表文件放入 download/ 目录"
fi

# 检查磁盘空间
echo "💾 检查磁盘空间..."
df -h /

echo ""
echo "✅ 部署完成！"
echo ""
echo "🎯 启动命令:"
echo "python3 sleep_data_manager_auth.py"
echo ""
echo "📊 监控命令:"
echo "tail -f uploaded_files.txt        # 查看上传进度"
echo "tail -f failed_downloads.txt      # 查看失败记录"
echo "df -h                             # 查看磁盘空间"
echo "" 