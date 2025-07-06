#!/usr/bin/env python3
"""
基于wget的PhysioNet下载器
使用wget进行认证下载，解决403权限问题
"""

import os
import subprocess
import time
import threading
import queue
from pathlib import Path
import shutil

class WgetDownloader:
    def __init__(self):
        # 从配置文件读取认证信息
        try:
            from dropbox_config import PHYSIONET_CONFIG, DROPBOX_CONFIG
            self.username = PHYSIONET_CONFIG['username']
            self.password = PHYSIONET_CONFIG['password']
            self.dropbox_token = DROPBOX_CONFIG['access_token']
        except ImportError:
            print("❌ 未找到 dropbox_config.py 配置文件")
            exit(1)
        
        # 路径配置
        self.download_dir = Path("download")
        self.download_dir.mkdir(exist_ok=True)
        
        # 状态文件
        self.success_log = "download_success.txt"
        self.uploaded_log = "uploaded_files.txt"
        self.failed_log = "failed_downloads.txt"
        
        # 配置
        self.max_workers = 3
        self.retry_attempts = 3
        self.timeout = 300
        
        # 队列和统计
        self.download_queue = queue.Queue()
        self.stats = {
            'downloaded': 0,
            'failed': 0,
            'skipped': 0,
            'total_size': 0
        }
        self.stats_lock = threading.Lock()
        
        print(f"🚀 Wget下载器初始化完成")
        print(f"🔐 用户: {self.username}")

    def load_existing_files(self):
        """加载已存在的文件记录"""
        downloaded = set()
        uploaded = set()
        
        # 已下载文件
        if os.path.exists(self.success_log):
            with open(self.success_log, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        downloaded.add(line)
        
        # 已上传文件
        if os.path.exists(self.uploaded_log):
            with open(self.uploaded_log, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        uploaded.add(line)
        
        # 本地文件
        local_files = set()
        for file_path in self.download_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.edf', '.tsv', '.atr']:
                if file_path.stat().st_size > 1000:  # 大于1KB
                    local_files.add(file_path.name)
        
        print(f"📊 已下载: {len(downloaded)}, 已上传: {len(uploaded)}, 本地: {len(local_files)}")
        return downloaded, uploaded, local_files

    def load_download_tasks(self):
        """加载下载任务"""
        print("📋 加载下载任务...")
        
        downloaded, uploaded, local_files = self.load_existing_files()
        skip_files = downloaded.union(uploaded).union(local_files)
        
        # 从list.txt加载URL
        tasks = []
        if os.path.exists("list.txt"):
            with open("list.txt", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        filename = line.split('/')[-1]
                        if filename not in skip_files:
                            tasks.append(line)
        
        # 添加到队列
        for url in tasks:
            self.download_queue.put(url)
        
        print(f"📥 待下载: {len(tasks)} 个文件")
        return len(tasks)

    def download_with_wget(self, url):
        """使用wget下载单个文件"""
        filename = url.split('/')[-1]
        file_path = self.download_dir / filename
        
        try:
            print(f"⬇️  下载: {filename}")
            
            # 构建wget命令
            cmd = [
                'wget',
                '-c',  # 断点续传
                '-t', str(self.retry_attempts),  # 重试次数
                '--timeout', str(self.timeout),  # 超时
                '--user', self.username,  # 用户名
                '--password', self.password,  # 密码
                '-O', str(file_path),  # 输出文件
                url
            ]
            
            # 执行wget命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 60  # 给wget额外的时间
            )
            
            if result.returncode == 0:
                # 检查文件大小
                if file_path.exists() and file_path.stat().st_size > 1000:
                    file_size = file_path.stat().st_size
                    
                    with self.stats_lock:
                        self.stats['downloaded'] += 1
                        self.stats['total_size'] += file_size
                    
                    # 记录成功
                    self.log_success(filename)
                    print(f"✅ 下载完成: {filename} ({file_size // 1024 // 1024}MB)")
                    return True
                else:
                    print(f"❌ 文件下载不完整: {filename}")
                    if file_path.exists():
                        file_path.unlink()
                    return False
            else:
                print(f"❌ wget失败: {filename}")
                print(f"   错误: {result.stderr}")
                if file_path.exists():
                    file_path.unlink()
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ 下载超时: {filename}")
            if file_path.exists():
                file_path.unlink()
            return False
        except Exception as e:
            print(f"❌ 下载异常: {filename} - {e}")
            if file_path.exists():
                file_path.unlink()
            return False

    def log_success(self, filename):
        """记录成功下载"""
        with open(self.success_log, 'a') as f:
            f.write(f"{filename}\n")

    def log_failure(self, url, error):
        """记录失败下载"""
        with open(self.failed_log, 'a') as f:
            f.write(f"{url} | {error}\n")

    def worker(self):
        """工作线程"""
        while True:
            try:
                url = self.download_queue.get(timeout=10)
                
                # 检查磁盘空间
                total, used, free = shutil.disk_usage("/")
                usage_percent = (used / total) * 100
                
                if usage_percent > 90:
                    print(f"⚠️  磁盘空间不足 ({usage_percent:.1f}%)，跳过下载")
                    self.download_queue.put(url)  # 放回队列
                    time.sleep(30)
                    continue
                
                # 下载文件
                success = self.download_with_wget(url)
                
                if not success:
                    with self.stats_lock:
                        self.stats['failed'] += 1
                    self.log_failure(url, "wget下载失败")
                
                self.download_queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                print(f"❌ 工作线程错误: {e}")

    def monitor_worker(self):
        """监控线程"""
        start_time = time.time()
        
        while True:
            time.sleep(60)  # 每分钟报告
            
            with self.stats_lock:
                elapsed = time.time() - start_time
                speed = self.stats['downloaded'] / (elapsed / 60) if elapsed > 0 else 0
                
                print(f"\n📊 进度报告 [{time.strftime('%H:%M:%S')}]:")
                print(f"   已下载: {self.stats['downloaded']} 个文件")
                print(f"   失败: {self.stats['failed']} 个文件")
                print(f"   跳过: {self.stats['skipped']} 个文件")
                print(f"   总大小: {self.stats['total_size'] // 1024 // 1024 // 1024:.2f}GB")
                print(f"   速度: {speed:.1f} 文件/分钟")
                print(f"   队列剩余: {self.download_queue.qsize()}")
                print("-" * 50)

    def run(self):
        """运行下载器"""
        print("🎯 启动Wget下载器")
        
        # 加载任务
        task_count = self.load_download_tasks()
        
        if task_count == 0:
            print("✅ 没有待下载任务")
            return
        
        # 启动工作线程
        threads = []
        
        for i in range(self.max_workers):
            t = threading.Thread(target=self.worker, name=f"Worker-{i+1}")
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_worker, name="Monitor")
        monitor_thread.daemon = True
        monitor_thread.start()
        threads.append(monitor_thread)
        
        print(f"🔄 启动 {len(threads)} 个线程")
        
        try:
            # 等待所有任务完成
            self.download_queue.join()
            
            print("\n🎉 所有下载任务完成！")
            
            with self.stats_lock:
                print(f"📊 最终统计:")
                print(f"   成功下载: {self.stats['downloaded']} 个文件")
                print(f"   失败: {self.stats['failed']} 个文件")
                print(f"   总大小: {self.stats['total_size'] // 1024 // 1024 // 1024:.2f}GB")
        
        except KeyboardInterrupt:
            print("\n⏹️  用户中断，正在退出...")
        except Exception as e:
            print(f"\n❌ 运行错误: {e}")

if __name__ == "__main__":
    downloader = WgetDownloader()
    downloader.run() 