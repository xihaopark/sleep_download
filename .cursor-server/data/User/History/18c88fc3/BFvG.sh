#!/bin/bash
# 部署测试脚本 - 验证系统是否正常工作

echo "======================================================================="
echo "🧪 PhysioNet Sleep Data Manager - 部署测试"
echo "======================================================================="

# 测试1: 检查必要文件
echo "📋 测试1: 检查必要文件..."
REQUIRED_FILES=("sleep_data_manager.py" "auto_upload_manager.py" "sensitive_config_template.py" "quick_start.sh" "manage.sh")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少文件: $file"
        exit 1
    fi
done
echo "✅ 所有必要文件存在"

# 测试2: 检查配置文件
echo "📋 测试2: 检查配置文件..."
if [ ! -f "dropbox_config.py" ]; then
    echo "⚠️  配置文件不存在，创建中..."
    cp sensitive_config_template.py dropbox_config.py
    echo "✅ 配置文件创建完成"
else
    echo "✅ 配置文件已存在"
fi

# 测试3: 检查Python依赖
echo "📋 测试3: 检查Python依赖..."
python3 -c "import requests, dropbox, json, time, os" 2>/dev/null || {
    echo "❌ Python依赖缺失"
    exit 1
}
echo "✅ Python依赖正常"

# 测试4: 检查配置文件语法
echo "📋 测试4: 检查配置文件语法..."
python3 -c "from dropbox_config import DROPBOX_CONFIG; print('Token长度:', len(DROPBOX_CONFIG['access_token']))" 2>/dev/null || {
    echo "❌ 配置文件语法错误"
    exit 1
}
echo "✅ 配置文件语法正常"

# 测试5: 检查脚本权限
echo "📋 测试5: 检查脚本权限..."
for script in "quick_start.sh" "manage.sh"; do
    if [ ! -x "$script" ]; then
        echo "⚠️  $script 没有执行权限，修复中..."
        chmod +x "$script"
    fi
done
echo "✅ 脚本权限正常"

# 测试6: 检查目录结构
echo "📋 测试6: 检查目录结构..."
mkdir -p download logs
echo "✅ 目录结构正常"

# 测试7: 检查现有数据
echo "📋 测试7: 检查现有数据..."
if [ -f "list.txt" ]; then
    LINK_COUNT=$(wc -l < list.txt)
    echo "✅ 发现 $LINK_COUNT 个下载链接"
else
    echo "⚠️  未找到 list.txt 文件"
fi

if [ -f "uploaded_files.txt" ]; then
    UPLOADED_COUNT=$(wc -l < uploaded_files.txt)
    echo "✅ 发现 $UPLOADED_COUNT 个已上传文件记录"
fi

if [ -f "download_success.txt" ]; then
    DOWNLOADED_COUNT=$(wc -l < download_success.txt)
    echo "✅ 发现 $DOWNLOADED_COUNT 个已下载文件记录"
fi

DOWNLOAD_FILES=$(ls -1 download 2>/dev/null | wc -l)
echo "✅ 下载目录包含 $DOWNLOAD_FILES 个文件"

# 测试8: 系统快速启动测试
echo "📋 测试8: 系统快速启动测试..."
echo "停止现有进程..."
./manage.sh stop > /dev/null 2>&1

echo "启动系统..."
./manage.sh start > /dev/null 2>&1

sleep 3

# 检查进程
PROCESS_COUNT=$(ps aux | grep -E "(sleep_data_manager|auto_upload_manager)" | grep -v grep | wc -l)
if [ $PROCESS_COUNT -gt 0 ]; then
    echo "✅ 系统启动成功，运行 $PROCESS_COUNT 个进程"
else
    echo "❌ 系统启动失败"
    exit 1
fi

echo ""
echo "======================================================================="
echo "🎉 部署测试完成！"
echo "======================================================================="
echo ""
echo "📊 系统摘要:"
echo "- 配置文件: ✅ 正常"
echo "- Python依赖: ✅ 正常"
echo "- 脚本权限: ✅ 正常"
echo "- 目录结构: ✅ 正常"
echo "- 进程状态: ✅ 运行中"
echo ""
echo "🚀 系统已准备就绪！"
echo ""
echo "常用命令:"
echo "  ./manage.sh status    # 查看状态"
echo "  ./manage.sh monitor   # 实时监控"
echo "  ./manage.sh logs      # 查看日志"
echo "  ./manage.sh restart   # 重启系统"
echo ""
echo "=======================================================================" 