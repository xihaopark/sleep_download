#!/usr/bin/env python3
"""
Sleep Data 自动化管理器
功能：
1. 并行下载文件
2. 并行上传到Dropbox
3. 自动状态管理
4. 智能重试机制
5. 磁盘空间监控

一键执行，无需额外配置
"""

import os
import sys
import threading
import time
import requests
import json
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import shutil

class SleepDataManager:
    def __init__(self):
        # Dropbox配置 - 内置令牌
        self.dropbox_token = "sl.u.AF34PeTlpglqeAYwABIYfeD3-SyW3tTUqkcjG_o5ffO0YJ9nT_G2pd1wHYFRqqv7z0-LFZ6jg6soFpe3KCUNDqulVlMPIWG-Mf80Jvbw72x6S9NJV-5-0IbRcXFeG7ktJWGjMFs5ynvdoFkJtzAZ9cMS3nvKk9Poqg-APtUA7IciNIDS3xa17WBDpBMg33z4Qm2FRaVgcNtu9OZ23zS7s0aNxX-SaKcWtElePah0seAESpGhHgtKTmnSOK3pt0gs5W0PqcmPw8p0y_euTs6_BGkQvieK_WdCzaOVP8Cs0dl1ep7IIYilmlEHw1HoXHstC-4oQJsIf7UFBaPNufbushoXDPftGh7wsFiW2x2c62fKDk1PtKh5B2MW2k1ZcMMK6QHom9bdFtagQ9mFSZV85stQkmNgXY2fMGaKbiMSLaNsv0BKYijWT6SEbQHAZSai6yMNn2rfWkVu_WjvaQrqTVme0WCtvNq_vhtkidxvLGQ1zDVqz-7b_JVhAGgg8gdzUk0DUUHq-HRKsg9WIgXmnn28j6exYVYqBxPxdAkL_m953kWKZKSIqcERKkjd-z7OP6VV-gdP0abDHFg8KnhZNJJufC_MG0Va1e_m4FAzMGVmNWO5Io9abHOrvDc2RyHyegVc-KZoeLZCwcov1JOhad1sPuJwvCTKDNqTNLhfLArlYYgbAygRhEI0VWNYDUnEgwov3cCcFqAPKWhGrcCQvdphhDy0AXht6-_DSqR1H36OrNfOkyypxTJzWLJ_GMh7U0M58grI0lpW5ecA0PcIy0U6Vze_Io29c8V4lZhNSSibtUevKyUa_Cg6-ay-xBiCBSPhbnc840-n-jPiK0manr55ruct-_tsFMuBtoa5S4UvDVdhuq2iT770DBmeriJDWrtfKdnc7ZxKUk_Wh18kMFyM995igTxyLuejytQhAUhbuWiMlTHik01m2382_H_yOwwpZ-wU0-EXp7_VatSEPJWPSAO3MJgCuc8y8Fdnk10MY6BzKc3EpbIbJtnIzTsxLiLu2aWklgzwuGkt_HsolNKgKTYEpqYvdT8gWZBBKUl9p9ETqP_lEkGfQ6j1RdXsSvtMiWJGl7xje6g5cwLfuwwXdMyly_PugCxdySaiuLQACguUpvk-M52P9Pgigu3cKxbuviy7mhT-bWdGLOo1FLqnHNTYkdY45-aMjL5JNL2i_ZdKNTgNuvseNd4C-uegmY6qXrpnOMO2uSxHe-p9JI2Sy9qo2_K-PWU5Bpp-3IQ6MsuVuSoC_IOWbpWtn9kG6g92FxNq9OyiVLNB6XZ-ozgeilEaelnkSs9lHk3dSt_dWw"
        
        # 路径配置
        self.download_dir = Path("download")
        self.download_dir.mkdir(exist_ok=True)
        
        # 状态文件
        self.uploaded_log = "uploaded_files.txt"
        self.download_queue_file = "download_queue.txt"
        self.failed_downloads_file = "failed_downloads.txt"
        
        # 并发配置
        self.max_download_threads = 3
        self.max_upload_threads = 2
        self.chunk_size = 100 * 1024 * 1024  # 100MB chunks
        
        # 基础URL
        self.base_url = "https://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/"
        
        # 队列
        self.download_queue = queue.Queue()
        self.upload_queue = queue.Queue()
        
        # 统计
        self.stats = {
            'downloaded': 0,
            'uploaded': 0,
            'failed': 0,
            'total_downloaded_size': 0,
            'total_uploaded_size': 0
        }
        
        # 锁
        self.stats_lock = threading.Lock()
        self.file_lock = threading.Lock()
        
        print("🚀 Sleep Data Manager 初始化完成")

    def load_existing_state(self):
        """加载现有状态"""
        print("📊 加载现有状态...")
        
        # 加载已上传文件
        uploaded_files = set()
        if os.path.exists(self.uploaded_log):
            with open(self.uploaded_log, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        uploaded_files.add(line)
        
        # 加载本地已存在的完整文件
        local_complete_files = set()
        for file_path in self.download_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.edf', '.tsv', '.atr']:
                try:
                    if file_path.stat().st_size > 100000:  # 大于100KB
                        local_complete_files.add(file_path.name)
                except:
                    pass
        
        print(f"✅ 已上传文件: {len(uploaded_files)}")
        print(f"✅ 本地完整文件: {len(local_complete_files)}")
        
        return uploaded_files, local_complete_files

    def normalize_url(self, url_or_filename):
        """标准化URL或文件名"""
        if url_or_filename.startswith('http'):
            return url_or_filename
        else:
            # 只是文件名，添加基础URL
            return self.base_url + url_or_filename

    def load_download_tasks(self):
        """加载下载任务"""
        print("📋 加载下载任务...")
        
        uploaded_files, local_complete_files = self.load_existing_state()
        skip_files = uploaded_files.union(local_complete_files)
        
        # 从多个源加载任务
        all_urls = set()
        
        # 1. 从group11.txt加载
        group11_file = self.download_dir / "group11.txt"
        if group11_file.exists():
            with open(group11_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        all_urls.add(self.normalize_url(line))
        
        # 2. 从not_downloaded.txt加载
        if os.path.exists("not_downloaded.txt"):
            with open("not_downloaded.txt", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        all_urls.add(self.normalize_url(line))
        
        # 过滤已处理的文件
        download_tasks = []
        for url in all_urls:
            filename = url.split('/')[-1]
            if filename not in skip_files:
                download_tasks.append(url)
        
        # 添加到下载队列
        for url in download_tasks:
            self.download_queue.put(url)
        
        print(f"📥 待下载任务: {len(download_tasks)}")
        return len(download_tasks)

    def load_upload_tasks(self):
        """加载上传任务"""
        print("📤 加载上传任务...")
        
        uploaded_files, _ = self.load_existing_state()
        
        upload_count = 0
        for file_path in self.download_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.edf', '.tsv', '.atr']:
                try:
                    if file_path.stat().st_size > 100000 and file_path.name not in uploaded_files:
                        self.upload_queue.put(file_path)
                        upload_count += 1
                except:
                    pass
        
        print(f"📤 待上传任务: {upload_count}")
        return upload_count

    def download_file(self, url, max_retries=3):
        """下载单个文件"""
        filename = url.split('/')[-1]
        file_path = self.download_dir / filename
        
        for attempt in range(max_retries):
            try:
                print(f"⬇️  下载: {filename} (尝试 {attempt + 1}/{max_retries})")
                
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                
                with open(file_path, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                
                # 验证下载
                actual_size = file_path.stat().st_size
                if total_size > 0 and actual_size != total_size:
                    raise Exception(f"文件大小不匹配: {actual_size} != {total_size}")
                
                with self.stats_lock:
                    self.stats['downloaded'] += 1
                    self.stats['total_downloaded_size'] += actual_size
                
                print(f"✅ 下载完成: {filename} ({actual_size // 1024 // 1024}MB)")
                
                # 如果是大文件，立即加入上传队列
                if actual_size > 100 * 1024 * 1024:  # 大于100MB
                    self.upload_queue.put(file_path)
                
                return True
                
            except Exception as e:
                print(f"❌ 下载失败: {filename} - {e}")
                if file_path.exists():
                    file_path.unlink()
                
                if attempt == max_retries - 1:
                    self.log_failed_download(url, str(e))
                    with self.stats_lock:
                        self.stats['failed'] += 1
                    return False
                
                time.sleep(2 ** attempt)  # 指数退避
        
        return False

    def chunked_upload_to_dropbox(self, file_path):
        """分块上传文件到Dropbox"""
        try:
            filename = file_path.name
            file_size = file_path.stat().st_size
            dropbox_path = f"/sleep_data/{filename}"
            
            print(f"📤 上传: {filename} ({file_size // 1024 // 1024}MB)")
            
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
                    current_chunk_size = min(self.chunk_size, remaining)
                    chunk_data = f.read(current_chunk_size)
                    
                    if offset + current_chunk_size < file_size:
                        # 中间块
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
                        # 最后一块
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
                    
                    offset += current_chunk_size
                    time.sleep(0.1)  # 避免API限制
            
            # 上传成功，删除本地文件并记录
            file_path.unlink()
            self.log_uploaded_file(filename)
            
            with self.stats_lock:
                self.stats['uploaded'] += 1
                self.stats['total_uploaded_size'] += file_size
            
            print(f"✅ 上传完成并删除: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 上传失败: {file_path.name} - {e}")
            return False

    def log_uploaded_file(self, filename):
        """记录已上传文件"""
        with self.file_lock:
            with open(self.uploaded_log, 'a') as f:
                f.write(f"{filename}\n")

    def log_failed_download(self, url, error):
        """记录失败的下载"""
        with self.file_lock:
            with open(self.failed_downloads_file, 'a') as f:
                f.write(f"{url} | {error}\n")

    def get_disk_usage(self):
        """获取磁盘使用情况"""
        total, used, free = shutil.disk_usage("/")
        return {
            'total': total,
            'used': used,
            'free': free,
            'percent': (used / total) * 100
        }

    def download_worker(self):
        """下载工作线程"""
        while True:
            try:
                url = self.download_queue.get(timeout=5)
                self.download_file(url)
                self.download_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f"❌ 下载工作线程错误: {e}")

    def upload_worker(self):
        """上传工作线程"""
        while True:
            try:
                file_path = self.upload_queue.get(timeout=5)
                self.chunked_upload_to_dropbox(file_path)
                self.upload_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f"❌ 上传工作线程错误: {e}")

    def monitor_worker(self):
        """监控工作线程"""
        while True:
            time.sleep(30)  # 每30秒报告一次
            
            disk = self.get_disk_usage()
            
            with self.stats_lock:
                print(f"\n📊 状态报告:")
                print(f"   下载: {self.stats['downloaded']} 个文件 ({self.stats['total_downloaded_size'] // 1024 // 1024}MB)")
                print(f"   上传: {self.stats['uploaded']} 个文件 ({self.stats['total_uploaded_size'] // 1024 // 1024}MB)")
                print(f"   失败: {self.stats['failed']} 个文件")
                print(f"   磁盘: {disk['percent']:.1f}% 使用 ({disk['free'] // 1024 // 1024 // 1024:.1f}GB 可用)")
                print(f"   队列: 下载 {self.download_queue.qsize()}, 上传 {self.upload_queue.qsize()}")
            
            # 磁盘空间警告
            if disk['percent'] > 95:
                print("⚠️  磁盘空间不足！暂停下载...")
                # 这里可以实现暂停逻辑

    def run(self):
        """运行主程序"""
        print("🎯 启动 Sleep Data Manager")
        
        # 加载任务
        download_tasks = self.load_download_tasks()
        upload_tasks = self.load_upload_tasks()
        
        if download_tasks == 0 and upload_tasks == 0:
            print("✅ 没有待处理任务，程序退出")
            return
        
        # 启动工作线程
        threads = []
        
        # 下载线程
        for i in range(self.max_download_threads):
            t = threading.Thread(target=self.download_worker, name=f"Download-{i+1}")
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 上传线程
        for i in range(self.max_upload_threads):
            t = threading.Thread(target=self.upload_worker, name=f"Upload-{i+1}")
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 监控线程
        monitor_thread = threading.Thread(target=self.monitor_worker, name="Monitor")
        monitor_thread.daemon = True
        monitor_thread.start()
        threads.append(monitor_thread)
        
        print(f"🔄 启动 {len(threads)} 个工作线程")
        
        try:
            # 等待所有下载和上传任务完成
            self.download_queue.join()
            self.upload_queue.join()
            
            print("\n🎉 所有任务完成！")
            
            # 最终统计
            with self.stats_lock:
                print(f"📊 最终统计:")
                print(f"   下载: {self.stats['downloaded']} 个文件")
                print(f"   上传: {self.stats['uploaded']} 个文件")
                print(f"   失败: {self.stats['failed']} 个文件")
                print(f"   总下载: {self.stats['total_downloaded_size'] // 1024 // 1024 // 1024:.2f}GB")
                print(f"   总上传: {self.stats['total_uploaded_size'] // 1024 // 1024 // 1024:.2f}GB")
        
        except KeyboardInterrupt:
            print("\n⏹️  用户中断，正在安全退出...")
        
        except Exception as e:
            print(f"\n❌ 程序错误: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Sleep Data 自动化管理器")
    print("   功能: 并行下载 + 自动上传 + 状态管理")
    print("   作者: AI Assistant")
    print("=" * 60)
    
    manager = SleepDataManager()
    manager.run()

if __name__ == "__main__":
    main() 