#!/bin/bash
# 快速进度查看脚本

echo "======================================================================="
echo "📊 项目进展快速查看 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================================================="

# 基本统计
TOTAL=$(wc -l < list.txt 2>/dev/null || echo 0)
DOWNLOADED=$(wc -l < download_success.txt 2>/dev/null || echo 0)
UPLOADED=$(wc -l < uploaded_files.txt 2>/dev/null || echo 0)
LOCAL=$(ls -1 download 2>/dev/null | wc -l)

# 计算进度
if [ $TOTAL -gt 0 ]; then
    DOWNLOAD_PERCENT=$((DOWNLOADED * 100 / TOTAL))
    UPLOAD_PERCENT=$((UPLOADED * 100 / TOTAL))
else
    DOWNLOAD_PERCENT=0
    UPLOAD_PERCENT=0
fi

# 显示进度
echo "📋 总体进度:"
echo "  总文件数: $TOTAL"
echo "  已下载: $DOWNLOADED ($DOWNLOAD_PERCENT%)"
echo "  已上传: $UPLOADED ($UPLOAD_PERCENT%)"
echo "  本地缓存: $LOCAL"
echo "  待处理: $((TOTAL - DOWNLOADED))"

# 简单进度条
echo ""
echo "📥 下载进度条:"
printf "  ["
for i in $(seq 1 20); do
    if [ $((i * 5)) -le $DOWNLOAD_PERCENT ]; then
        printf "█"
    else
        printf "░"
    fi
done
printf "] $DOWNLOAD_PERCENT%%\n"

echo ""
echo "📤 上传进度条:"
printf "  ["
for i in $(seq 1 20); do
    if [ $((i * 5)) -le $UPLOAD_PERCENT ]; then
        printf "█"
    else
        printf "░"
    fi
done
printf "] $UPLOAD_PERCENT%%\n"

# 系统状态
echo ""
echo "🔄 系统状态:"
if pgrep -f "sleep_data_manager" > /dev/null; then
    echo "  ✅ 下载管理器: 运行中"
else
    echo "  ❌ 下载管理器: 未运行"
fi

if pgrep -f "auto_upload_manager" > /dev/null; then
    echo "  ✅ 上传管理器: 运行中"
else
    echo "  ❌ 上传管理器: 未运行"
fi

# 磁盘使用
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}')
DISK_AVAIL=$(df -h . | tail -1 | awk '{print $4}')
echo "  💾 磁盘使用: $DISK_USAGE (可用: $DISK_AVAIL)"

# 最新活动
echo ""
echo "📋 最新活动:"
if [ -f "logs/download_manager.log" ]; then
    echo "  🔽 最新下载:"
    tail -2 logs/download_manager.log | head -1 | sed 's/^/    /'
fi

echo ""
echo "=======================================================================" 