#!/bin/bash
# 实时进度监控脚本

echo "======================================================================="
echo "📊 PhysioNet Sleep Data Manager - 实时进度监控"
echo "======================================================================="
echo "按 Ctrl+C 退出监控"
echo ""

# 初始化计数器
LAST_DOWNLOADED=0
LAST_UPLOADED=0
START_TIME=$(date +%s)

while true; do
    clear
    echo "======================================================================="
    echo "📊 实时进度监控 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "======================================================================="
    
    # 获取当前统计
    TOTAL_LINKS=$(wc -l < list.txt 2>/dev/null || echo 0)
    DOWNLOADED=$(wc -l < download_success.txt 2>/dev/null || echo 0)
    UPLOADED=$(wc -l < uploaded_files.txt 2>/dev/null || echo 0)
    LOCAL_FILES=$(ls -1 download 2>/dev/null | wc -l)
    
    # 计算进度
    if [ $TOTAL_LINKS -gt 0 ]; then
        DOWNLOAD_PERCENT=$((DOWNLOADED * 100 / TOTAL_LINKS))
        UPLOAD_PERCENT=$((UPLOADED * 100 / TOTAL_LINKS))
    else
        DOWNLOAD_PERCENT=0
        UPLOAD_PERCENT=0
    fi
    
    # 计算速度
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    if [ $ELAPSED -gt 0 ]; then
        DOWNLOAD_SPEED=$(((DOWNLOADED - LAST_DOWNLOADED) * 60 / 10))  # 每分钟
        UPLOAD_SPEED=$(((UPLOADED - LAST_UPLOADED) * 60 / 10))       # 每分钟
    else
        DOWNLOAD_SPEED=0
        UPLOAD_SPEED=0
    fi
    
    # 显示进度条
    echo "📥 下载进度: $DOWNLOADED/$TOTAL_LINKS ($DOWNLOAD_PERCENT%)"
    printf "["
    for i in $(seq 1 50); do
        if [ $((i * 2)) -le $DOWNLOAD_PERCENT ]; then
            printf "█"
        else
            printf "░"
        fi
    done
    printf "] $DOWNLOAD_SPEED 文件/分钟\n"
    
    echo ""
    echo "📤 上传进度: $UPLOADED/$TOTAL_LINKS ($UPLOAD_PERCENT%)"
    printf "["
    for i in $(seq 1 50); do
        if [ $((i * 2)) -le $UPLOAD_PERCENT ]; then
            printf "█"
        else
            printf "░"
        fi
    done
    printf "] $UPLOAD_SPEED 文件/分钟\n"
    
    echo ""
    echo "======================================================================="
    echo "📊 详细统计"
    echo "======================================================================="
    echo "总链接数: $TOTAL_LINKS"
    echo "已下载: $DOWNLOADED 个文件"
    echo "已上传: $UPLOADED 个文件"
    echo "本地缓存: $LOCAL_FILES 个文件"
    echo "待下载: $((TOTAL_LINKS - DOWNLOADED)) 个文件"
    echo "待上传: $((DOWNLOADED - UPLOADED)) 个文件"
    
    # 磁盘使用情况
    DISK_INFO=$(df -h . | tail -1)
    DISK_USED=$(echo $DISK_INFO | awk '{print $5}')
    DISK_AVAIL=$(echo $DISK_INFO | awk '{print $4}')
    echo "磁盘使用: $DISK_USED (可用: $DISK_AVAIL)"
    
    # 运行时间
    RUNTIME=$((ELAPSED / 60))
    echo "运行时间: ${RUNTIME} 分钟"
    
    # 进程状态
    echo ""
    echo "======================================================================="
    echo "🔄 进程状态"
    echo "======================================================================="
    DOWNLOAD_PROCESS=$(ps aux | grep -E "sleep_data_manager\.py" | grep -v grep | wc -l)
    UPLOAD_PROCESS=$(ps aux | grep -E "auto_upload_manager\.py" | grep -v grep | wc -l)
    
    if [ $DOWNLOAD_PROCESS -gt 0 ]; then
        echo "✅ 下载管理器: 运行中"
    else
        echo "❌ 下载管理器: 未运行"
    fi
    
    if [ $UPLOAD_PROCESS -gt 0 ]; then
        echo "✅ 上传管理器: 运行中"
    else
        echo "❌ 上传管理器: 未运行"
    fi
    
    # 最新活动
    echo ""
    echo "======================================================================="
    echo "📋 最新活动 (最后3行)"
    echo "======================================================================="
    if [ -f "logs/download_manager.log" ]; then
        echo "🔽 下载日志:"
        tail -3 logs/download_manager.log | sed 's/^/   /'
    fi
    
    if [ -f "logs/upload_manager.log" ]; then
        echo ""
        echo "🔼 上传日志:"
        tail -3 logs/upload_manager.log | sed 's/^/   /'
    fi
    
    echo ""
    echo "======================================================================="
    echo "⏱️  下次更新: 10秒后 | 按 Ctrl+C 退出"
    echo "======================================================================="
    
    # 更新计数器
    LAST_DOWNLOADED=$DOWNLOADED
    LAST_UPLOADED=$UPLOADED
    
    # 等待10秒
    sleep 10
done 