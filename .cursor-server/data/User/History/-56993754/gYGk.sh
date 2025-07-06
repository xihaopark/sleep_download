#!/bin/bash
# PhysioNet Sleep Data Manager - 管理脚本

case "$1" in
    status)
        echo "======================================================================="
        echo "📊 系统状态"
        echo "======================================================================="
        echo ""
        echo "=== 进程状态 ==="
        PROCESSES=$(ps aux | grep -E "sleep_data_wget_manager" | grep -v grep)
        if [ -n "$PROCESSES" ]; then
            echo "$PROCESSES"
        else
            echo "❌ 没有运行的进程"
        fi
        
        echo ""
        echo "=== 文件状态 ==="
        echo "下载目录: $(ls -1 download 2>/dev/null | wc -l) 个文件"
        echo "总链接数: $(wc -l < list.txt 2>/dev/null || echo 0)"
        echo "已下载: $(wc -l < download_success.txt 2>/dev/null || echo 0)"
        echo "已上传: $(wc -l < uploaded_files.txt 2>/dev/null || echo 0)"
        
        echo ""
        echo "=== 磁盘状态 ==="
        df -h . | tail -1
        
        echo ""
        echo "=== 最新日志 ==="
        if [ -f "logs/wget_manager.log" ]; then
            echo "Wget管理器日志 (最后5行):"
            tail -5 logs/wget_manager.log
        fi
        ;;
        
    stop)
        echo "🛑 停止所有进程..."
        pkill -f sleep_data_wget_manager && echo "✅ 停止Wget管理器" || echo "⚠️  Wget管理器未运行"
        echo "✅ 所有进程已停止"
        ;;
        
    start)
        echo "🚀 启动Wget管理器..."
        
        # 创建日志目录
        mkdir -p logs
        
        # 启动wget管理器
        if ! pgrep -f sleep_data_wget_manager > /dev/null; then
            nohup python3 sleep_data_wget_manager.py > logs/wget_manager.log 2>&1 &
            echo "✅ 启动Wget管理器 (PID: $!)"
        else
            echo "⚠️  Wget管理器已在运行"
        fi
        
        sleep 2
        echo "✅ 启动完成"
        ;;
        
    restart)
        echo "🔄 重启系统..."
        $0 stop
        sleep 3
        $0 start
        ;;
        
    logs)
        echo "======================================================================="
        echo "📄 系统日志"
        echo "======================================================================="
        
        if [ -f "logs/wget_manager.log" ]; then
            echo ""
            echo "=== Wget管理器日志 (最后20行) ==="
            tail -20 logs/wget_manager.log
        fi
        ;;
        
    clean)
        echo "🧹 清理系统..."
        
        # 清理空文件
        find download -type f -size 0 -delete 2>/dev/null && echo "✅ 清理了空文件" || true
        
        # 清理旧日志
        if [ -f "logs/wget_manager.log" ]; then
            tail -1000 logs/wget_manager.log > logs/wget_manager.log.tmp
            mv logs/wget_manager.log.tmp logs/wget_manager.log
            echo "✅ 清理了Wget管理器日志"
        fi
        
        echo "✅ 清理完成"
        ;;
        
    monitor)
        echo "👁️  实时监控 (按Ctrl+C退出)..."
        while true; do
            clear
            $0 status
            sleep 10
        done
        ;;
        
    *)
        echo "======================================================================="
        echo "🛠️  PhysioNet Sleep Data Manager - 管理工具"
        echo "======================================================================="
        echo ""
        echo "用法: $0 {command}"
        echo ""
        echo "命令:"
        echo "  status    - 查看系统状态"
        echo "  start     - 启动所有进程"
        echo "  stop      - 停止所有进程"
        echo "  restart   - 重启所有进程"
        echo "  logs      - 查看详细日志"
        echo "  clean     - 清理系统文件"
        echo "  monitor   - 实时监控状态"
        echo ""
        echo "示例:"
        echo "  $0 status     # 查看当前状态"
        echo "  $0 restart    # 重启系统"
        echo "  $0 monitor    # 开始监控"
        echo "======================================================================="
        ;;
esac 