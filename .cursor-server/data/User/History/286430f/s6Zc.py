#!/usr/bin/env python3
"""
完整的PhysioNet睡眠数据管理器 - Wget版本
功能：wget下载 + Dropbox上传 + 容量管理 + 防重复
"""

import os
import subprocess
import time
import threading
import queue
import json
import requests
import shutil
from pathlib import Path

class SleepDataWgetManager:
    def __init__(self):
        # 从配置文件读取
        try:
            from dropbox_config import PHYSIONET_CONFIG, DROPBOX_CONFIG, DOWNLOAD_CONFIG, UPLOAD_CONFIG
            self.username = PHYSIONET_CONFIG['username']
            self.password = PHYSIONET_CONFIG['password']
            self.upload_folder = DROPBOX_CONFIG['upload_folder']
            self.max_concurrent = DOWNLOAD_CONFIG.get('max_concurrent_downloads', 3)
            self.retry_attempts = DOWNLOAD_CONFIG.get('retry_attempts', 3)
            self.timeout = DOWNLOAD_CONFIG.get('download_timeout', 300)
            self.min_free_gb = DOWNLOAD_CONFIG.get('min_free_space_gb', 5)
            self.delete_after_upload = UPLOAD_CONFIG.get('delete_after_upload', True)
            self.chunk_size = UPLOAD_CONFIG.get('upload_chunk_size', 8*1024*1024)
            
            # 使用token管理器获取有效token
            self.dropbox_token = self.get_valid_token()
            if not self.dropbox_token:
                print("❌ 无法获取有效的Dropbox token")
                exit(1)
                
        except ImportError:
            print("❌ 未找到配置文件")
            exit(1)
        
        # 路径和文件
        self.download_dir = Path("download")
        self.download_dir.mkdir(exist_ok=True)
        self.success_log = "download_success.txt"
        self.uploaded_log = "uploaded_files.txt"
        self.failed_log = "failed_downloads.txt"
        
        # 队列
        self.download_queue = queue.Queue()
        self.upload_queue = queue.Queue()
        
        # 统计
        self.stats = {
            'downloaded': 0, 'uploaded': 0, 'failed': 0, 'skipped': 0,
            'download_size': 0, 'upload_size': 0
        }
        self.stats_lock = threading.Lock()
        
        print(f"🚀 睡眠数据管理器 (Wget版) 初始化完成")
        print(f"🔐 用户: {self.username}")

    def get_valid_token(self):
        """获取有效的Dropbox token"""
        try:
            # 尝试使用token管理器
            from token_manager import MultiServerTokenManager
            manager = MultiServerTokenManager()
            token_data = manager.get_current_token()
            
            if token_data:
                return token_data['access_token']
            else:
                print("⚠️  Token管理器未找到有效token，尝试从配置文件读取...")
                # 备用方案：从配置文件读取
                from dropbox_config import DROPBOX_CONFIG
                return DROPBOX_CONFIG['access_token']
                
        except Exception as e:
            print(f"⚠️  Token管理器加载失败: {e}")
            try:
                # 备用方案：从配置文件读取
                from dropbox_config import DROPBOX_CONFIG
                return DROPBOX_CONFIG['access_token']
            except:
                return None

    def load_existing_state(self):
        """加载现有状态"""
        downloaded = set()
        uploaded = set()
        
        if os.path.exists(self.success_log):
            with open(self.success_log, 'r') as f:
                downloaded = {line.strip() for line in f if line.strip()}
        
        if os.path.exists(self.uploaded_log):
            with open(self.uploaded_log, 'r') as f:
                uploaded = {line.strip() for line in f if line.strip()}
        
        local_files = set()
        for file_path in self.download_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.edf', '.tsv', '.atr']:
                if file_path.stat().st_size > 1000:
                    local_files.add(file_path.name)
        
        print(f"📊 已下载: {len(downloaded)}, 已上传: {len(uploaded)}, 本地: {len(local_files)}")
        return downloaded, uploaded, local_files

    def load_tasks(self):
        """加载任务"""
        downloaded, uploaded, local_files = self.load_existing_state()
        skip_files = downloaded.union(uploaded).union(local_files)
        
        # 加载下载任务
        download_tasks = []
        if os.path.exists("list.txt"):
            with open("list.txt", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        filename = line.split('/')[-1]
                        if filename not in skip_files:
                            download_tasks.append(line)
        
        # 加载上传任务
        upload_tasks = []
        for file_path in self.download_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.edf', '.tsv', '.atr']:
                if file_path.stat().st_size > 1000 and file_path.name not in uploaded:
                    upload_tasks.append(file_path)
        
        # 按大小排序，优先处理大文件
        upload_tasks.sort(key=lambda x: x.stat().st_size, reverse=True)
        
        # 添加到队列
        for url in download_tasks:
            self.download_queue.put(url)
        for file_path in upload_tasks:
            self.upload_queue.put(file_path)
        
        print(f"📥 待下载: {len(download_tasks)}, 📤 待上传: {len(upload_tasks)}")
        return len(download_tasks), len(upload_tasks)

    def check_disk_space(self):
        """检查磁盘空间"""
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        usage_percent = (used / total) * 100
        return free_gb, usage_percent

    def download_with_wget(self, url):
        """使用wget下载"""
        filename = url.split('/')[-1]
        file_path = self.download_dir / filename
        
        try:
            print(f"⬇️  下载: {filename}")
            
            cmd = [
                'wget', '-c', '-t', str(self.retry_attempts),
                '--timeout', str(self.timeout),
                '--user', self.username, '--password', self.password,
                '-O', str(file_path), url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout+60)
            
            if result.returncode == 0 and file_path.exists() and file_path.stat().st_size > 1000:
                size = file_path.stat().st_size
                with self.stats_lock:
                    self.stats['downloaded'] += 1
                    self.stats['download_size'] += size
                
                with open(self.success_log, 'a') as f:
                    f.write(f"{filename}\n")
                
                print(f"✅ 下载完成: {filename} ({size//1024//1024}MB)")
                
                # 大文件立即加入上传队列
                if size > 50*1024*1024:
                    self.upload_queue.put(file_path)
                
                return True
            else:
                if file_path.exists():
                    file_path.unlink()
                return False
                
        except Exception as e:
            print(f"❌ 下载失败: {filename} - {e}")
            if file_path.exists():
                file_path.unlink()
            return False

    def upload_to_dropbox(self, file_path):
        """上传到Dropbox"""
        try:
            filename = file_path.name
            file_size = file_path.stat().st_size
            dropbox_path = f"{self.upload_folder}/{filename}"
            
            print(f"📤 上传: {filename} ({file_size//1024//1024}MB)")
            
            with open(file_path, 'rb') as f:
                # 开始上传会话
                start_response = requests.post(
                    'https://content.dropboxapi.com/2/files/upload_session/start',
                    headers={
                        'Authorization': f'Bearer {self.dropbox_token}',
                        'Dropbox-API-Arg': json.dumps({}),
                        'Content-Type': 'application/octet-stream'
                    },
                    data=f.read(self.chunk_size),
                    timeout=300
                )
                
                if start_response.status_code != 200:
                    raise Exception(f"开始上传失败: {start_response.status_code}")
                
                session_id = start_response.json()['session_id']
                offset = self.chunk_size
                
                # 上传剩余块
                while offset < file_size:
                    remaining = file_size - offset
                    current_chunk = min(self.chunk_size, remaining)
                    chunk_data = f.read(current_chunk)
                    
                    if offset + current_chunk < file_size:
                        append_response = requests.post(
                            'https://content.dropboxapi.com/2/files/upload_session/append_v2',
                            headers={
                                'Authorization': f'Bearer {self.dropbox_token}',
                                'Dropbox-API-Arg': json.dumps({
                                    'cursor': {'session_id': session_id, 'offset': offset}
                                }),
                                'Content-Type': 'application/octet-stream'
                            },
                            data=chunk_data,
                            timeout=300
                        )
                        if append_response.status_code != 200:
                            raise Exception(f"块上传失败: {append_response.status_code}")
                    else:
                        finish_response = requests.post(
                            'https://content.dropboxapi.com/2/files/upload_session/finish',
                            headers={
                                'Authorization': f'Bearer {self.dropbox_token}',
                                'Dropbox-API-Arg': json.dumps({
                                    'cursor': {'session_id': session_id, 'offset': offset},
                                    'commit': {'path': dropbox_path, 'mode': 'add', 'autorename': True}
                                }),
                                'Content-Type': 'application/octet-stream'
                            },
                            data=chunk_data,
                            timeout=300
                        )
                        if finish_response.status_code != 200:
                            raise Exception(f"完成上传失败: {finish_response.status_code}")
                    
                    offset += current_chunk
                    time.sleep(0.1)
            
            # 记录上传成功
            with open(self.uploaded_log, 'a') as f:
                f.write(f"{filename}\n")
            
            with self.stats_lock:
                self.stats['uploaded'] += 1
                self.stats['upload_size'] += file_size
            
            # 删除本地文件
            if self.delete_after_upload:
                file_path.unlink()
                print(f"✅ 上传完成并删除: {filename}")
            else:
                print(f"✅ 上传完成: {filename}")
            
            return True
            
        except Exception as e:
            print(f"❌ 上传失败: {file_path.name} - {e}")
            return False

    def download_worker(self):
        """下载工作线程"""
        while True:
            try:
                url = self.download_queue.get(timeout=10)
                
                # 检查磁盘空间
                free_gb, usage_percent = self.check_disk_space()
                if free_gb < self.min_free_gb:
                    print(f"⚠️  磁盘空间不足 ({free_gb:.1f}GB)，暂停下载")
                    self.download_queue.put(url)
                    time.sleep(30)
                    continue
                
                success = self.download_with_wget(url)
                if not success:
                    with self.stats_lock:
                        self.stats['failed'] += 1
                
                self.download_queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                print(f"❌ 下载线程错误: {e}")

    def upload_worker(self):
        """上传工作线程"""
        while True:
            try:
                file_path = self.upload_queue.get(timeout=10)
                self.upload_to_dropbox(file_path)
                self.upload_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f"❌ 上传线程错误: {e}")

    def monitor_worker(self):
        """监控线程"""
        start_time = time.time()
        while True:
            time.sleep(60)
            
            free_gb, usage_percent = self.check_disk_space()
            elapsed = time.time() - start_time
            
            with self.stats_lock:
                download_speed = self.stats['downloaded'] / (elapsed/60) if elapsed > 0 else 0
                upload_speed = self.stats['uploaded'] / (elapsed/60) if elapsed > 0 else 0
                
                print(f"\n📊 状态报告 [{time.strftime('%H:%M:%S')}]:")
                print(f"   已下载: {self.stats['downloaded']} ({self.stats['download_size']//1024//1024//1024:.1f}GB)")
                print(f"   已上传: {self.stats['uploaded']} ({self.stats['upload_size']//1024//1024//1024:.1f}GB)")
                print(f"   失败: {self.stats['failed']} | 跳过: {self.stats['skipped']}")
                print(f"   速度: ⬇️{download_speed:.1f}/min ⬆️{upload_speed:.1f}/min")
                print(f"   队列: 下载{self.download_queue.qsize()} 上传{self.upload_queue.qsize()}")
                print(f"   磁盘: {usage_percent:.1f}% 使用 ({free_gb:.1f}GB 可用)")
                print("-" * 60)

    def run(self):
        """运行管理器"""
        print("🎯 启动睡眠数据管理器 (Wget版)")
        
        download_tasks, upload_tasks = self.load_tasks()
        
        if download_tasks == 0 and upload_tasks == 0:
            print("✅ 没有待处理任务")
            return
        
        # 启动线程
        threads = []
        
        # 下载线程
        for i in range(self.max_concurrent):
            t = threading.Thread(target=self.download_worker, name=f"Download-{i+1}")
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 上传线程
        t = threading.Thread(target=self.upload_worker, name="Upload")
        t.daemon = True
        t.start()
        threads.append(t)
        
        # 监控线程
        t = threading.Thread(target=self.monitor_worker, name="Monitor")
        t.daemon = True
        t.start()
        threads.append(t)
        
        print(f"🔄 启动 {len(threads)} 个线程")
        
        try:
            # 等待完成
            self.download_queue.join()
            self.upload_queue.join()
            
            print("\n🎉 所有任务完成！")
            
            with self.stats_lock:
                print(f"📊 最终统计:")
                print(f"   下载: {self.stats['downloaded']} 个文件 ({self.stats['download_size']//1024//1024//1024:.2f}GB)")
                print(f"   上传: {self.stats['uploaded']} 个文件 ({self.stats['upload_size']//1024//1024//1024:.2f}GB)")
                print(f"   失败: {self.stats['failed']} 个文件")
        
        except KeyboardInterrupt:
            print("\n⏹️  用户中断")
        except Exception as e:
            print(f"\n❌ 运行错误: {e}")

if __name__ == "__main__":
    manager = SleepDataWgetManager()
    manager.run() 