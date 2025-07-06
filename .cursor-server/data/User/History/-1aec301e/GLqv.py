#!/usr/bin/env python3
"""
Sleep Data 自动化管理器 - 认证版本
功能：
1. 并行下载文件（带认证）
2. 并行上传到Dropbox
3. 自动状态管理
4. 智能重试机制
5. 磁盘空间监控

一键执行，包含认证信息
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
from requests.auth import HTTPBasicAuth

class SleepDataManagerAuth:
    def __init__(self):
        # PhysioNet认证信息
        self.physionet_username = "chenzcha"  # 你的PhysioNet用户名
        self.physionet_password = "97HU15lWcE"  # 提供的密码
        
        # Dropbox配置 - 内置令牌
        self.dropbox_token = "sl.u.AF0ZhY-38erhzFdrLPJvKAvQL3V4tFwKeK3LFCU7CIVub5KH-lBYZJje050AZ-qDY5fTqMHdMrTQOTBph2IZPNFz2tleHtAtPUR4m16XSoSaG5vFQ1GcEySeadFY7hbtZqaYyrnxmcvT2VTR35xYo2o8xAqHIlLo3qjEe71Y0mdG80Or1g3RtPKJXkIxzO9dHqrcT_Jul3gSGuljMr6rfzNYhJUQPU_PfbbhCXXMQs_IpqYa7wawSSuXtS2SLrxmoYfPFSaAhmKIDv4N7qale0AOHdjuh5-e8p5WDwdE_JqSJCbsSZlmGl-t0O3UsxHaMGjCoqy3MpDVYR2_XOPEWheLPrbKIwao6_2KKLrxvh--5oKlgE1NG4da1EVwGSQMK7g5rYHZkg1yEnWP5fHyLU8VOT8fdC6e5FIcKIC6HnvDmwzF0MTEnxkFGU9NQW5GULvDBTI8CFXRhg9sAK6StvwCft_uEtbpe1Piu3sG_AVd12G7R_wJggInGRWyN3SQBoGK5Lmtey5YWhTPvBXw-aqE37XYFJuC3VQl06cbVOIdrMi33YhdeoMiB3eLBCUt6H2Te619LzG_b6jixmH1nHmvyVcp4vGHUbNd8b_R8ffd2VooeX8UyDUAGZiYbSn4czgNGLoiPa_g7NG3RCeKz1JevcTbnQd_ynFhSs2eYonkIosSDy8XGuwXuLKvqPkH77NTerLNx8ogzk-Dy-a_E4XbZSSf9GrMGVOqr2NKk2yAmUoK6E4pZ_T6ZFAP6UKhJQJd0YPEHHD5sDY-2uJJccWlzVkN62qY_Z6GNVB94raiQEkxPSCea4Pcd9SxdKSmedEbXtCffKPYqp2BgEWpwfI_VcYegzO4dmu-35GwArPIWRmdHRG_WcYr9zUMo1gKapiHDDRutEY8BAgtN9BUs17an9dI20fSaKexBC4c7TQ-TxxpqOPsDOXgrKLZQrB7CXplfnlJZwb7L8LWS8LrIqmLhPp8F-WfiQSAGm-qdGCAmVmFqk_FeBGp9CTbe5dVx256JX-Bg56Napz15BohD6cZCoTlv5PpPBrHCx_tRYysd3MF4NYTuu5Zpnsjg5C9WetPGB_W1GLfh4QKPB70OCXRhCPM290VRn5rotm0t7c3_DFxI6fodsZ8R18xfFSnN7yg-hn9-iEHvb69K2havWfp4KQY_MCXBE8BnDFVvN6C5wNsuOnzu0MJUP4vdwhRYc54ZOeJjxtanaOcWXGlWhq9uoFhSqRM1cdjoTUxTTEqZG799fgPfFj-JNNjJHEQe-j-iZGOMYAm8ZCp8MU97V99-gXguu6kUMAYpAUUVpMumg"
        
        # 路径配置
        self.download_dir = Path("download")
        self.download_dir.mkdir(exist_ok=True)
        
        # 状态文件
        self.uploaded_log = "uploaded_files.txt"
        self.download_queue_file = "download_queue.txt"
        self.failed_downloads_file = "failed_downloads.txt"
        self.success_log = "download_success.txt"
        
        # 并发配置
        self.max_download_threads = 4
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
            'skipped': 0,
            'total_downloaded_size': 0,
            'total_uploaded_size': 0
        }
        
        # 锁
        self.stats_lock = threading.Lock()
        self.file_lock = threading.Lock()
        
        print("🚀 Sleep Data Manager (认证版) 初始化完成")
        print(f"🔐 使用认证: {self.physionet_username}")

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
        
        # 加载已成功下载的文件
        downloaded_files = set()
        if os.path.exists(self.success_log):
            with open(self.success_log, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        downloaded_files.add(line)
        
        # 加载本地已存在的完整文件
        local_complete_files = set()
        for file_path in self.download_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.edf', '.tsv', '.atr']:
                try:
                    if file_path.stat().st_size > 10000:  # 大于10KB
                        local_complete_files.add(file_path.name)
                except:
                    pass
        
        print(f"✅ 已上传文件: {len(uploaded_files)}")
        print(f"✅ 已下载文件: {len(downloaded_files)}")
        print(f"✅ 本地完整文件: {len(local_complete_files)}")
        
        return uploaded_files, downloaded_files, local_complete_files

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
        
        uploaded_files, downloaded_files, local_complete_files = self.load_existing_state()
        skip_files = uploaded_files.union(downloaded_files).union(local_complete_files)
        
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
        
        # 优先下载EDF文件（大文件）
        edf_tasks = [url for url in download_tasks if url.endswith('.edf')]
        other_tasks = [url for url in download_tasks if not url.endswith('.edf')]
        
        # 添加到下载队列
        for url in edf_tasks + other_tasks:
            self.download_queue.put(url)
        
        print(f"📥 待下载任务: {len(download_tasks)} (EDF: {len(edf_tasks)}, 其他: {len(other_tasks)})")
        return len(download_tasks)

    def load_upload_tasks(self):
        """加载上传任务"""
        print("📤 加载上传任务...")
        
        uploaded_files, _, _ = self.load_existing_state()
        
        upload_count = 0
        upload_tasks = []
        
        for file_path in self.download_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.edf', '.tsv', '.atr']:
                try:
                    if file_path.stat().st_size > 10000 and file_path.name not in uploaded_files:
                        upload_tasks.append((file_path, file_path.stat().st_size))
                        upload_count += 1
                except:
                    pass
        
        # 按文件大小排序，优先上传大文件
        upload_tasks.sort(key=lambda x: x[1], reverse=True)
        
        for file_path, _ in upload_tasks:
            self.upload_queue.put(file_path)
        
        print(f"📤 待上传任务: {upload_count}")
        return upload_count

    def download_file(self, url, max_retries=3):
        """下载单个文件（带认证）"""
        filename = url.split('/')[-1]
        file_path = self.download_dir / filename
        
        # 检查文件是否已存在，支持断点续传
        resume_pos = 0
        if file_path.exists():
            try:
                resume_pos = file_path.stat().st_size
                if resume_pos > 10000:
                    # 先检查文件是否完整
                    print(f"🔍 检查已存在文件: {filename} ({resume_pos // 1024 // 1024}MB)")
                    
                    # 发送HEAD请求获取文件大小
                    auth = HTTPBasicAuth(self.physionet_username, self.physionet_password)
                    head_response = requests.head(url, auth=auth, timeout=30)
                    if head_response.status_code == 200:
                        total_size = int(head_response.headers.get('content-length', 0))
                        if total_size > 0 and resume_pos >= total_size:
                            print(f"✅ 文件已完整: {filename}")
                            with self.stats_lock:
                                self.stats['skipped'] += 1
                            return True
                        elif total_size > 0 and resume_pos > 0:
                            print(f"📥 断点续传: {filename} (从 {resume_pos // 1024 // 1024}MB 开始)")
            except:
                resume_pos = 0
        
        for attempt in range(max_retries):
            try:
                print(f"⬇️  下载: {filename} (尝试 {attempt + 1}/{max_retries})")
                
                # 使用认证信息，模拟wget行为
                auth = HTTPBasicAuth(self.physionet_username, self.physionet_password)
                
                response = requests.get(
                    url, 
                    stream=True, 
                    timeout=300,  # 300秒超时，对应wget --timeout=300
                    auth=auth,
                    headers={
                        'User-Agent': 'Wget/1.20.3 (linux-gnu)',  # 模拟wget
                        'Accept': '*/*',
                        'Accept-Encoding': 'identity',
                        'Connection': 'Keep-Alive'
                    },
                    allow_redirects=True
                )
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
                if total_size > 0 and abs(actual_size - total_size) > 1024:  # 允许1KB误差
                    raise Exception(f"文件大小不匹配: {actual_size} != {total_size}")
                
                with self.stats_lock:
                    self.stats['downloaded'] += 1
                    self.stats['total_downloaded_size'] += actual_size
                
                # 记录成功下载
                self.log_successful_download(filename)
                
                print(f"✅ 下载完成: {filename} ({actual_size // 1024 // 1024}MB)")
                
                # 如果是大文件，立即加入上传队列
                if actual_size > 50 * 1024 * 1024:  # 大于50MB
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

    def log_successful_download(self, filename):
        """记录成功下载的文件"""
        with self.file_lock:
            with open(self.success_log, 'a') as f:
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
                url = self.download_queue.get(timeout=10)
                
                # 检查磁盘空间
                disk = self.get_disk_usage()
                if disk['percent'] > 90:
                    print(f"⚠️  磁盘空间不足 ({disk['percent']:.1f}%)，暂停下载")
                    self.download_queue.put(url)  # 放回队列
                    time.sleep(30)
                    continue
                
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
                file_path = self.upload_queue.get(timeout=10)
                self.chunked_upload_to_dropbox(file_path)
                self.upload_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f"❌ 上传工作线程错误: {e}")

    def monitor_worker(self):
        """监控工作线程"""
        while True:
            time.sleep(60)  # 每60秒报告一次
            
            disk = self.get_disk_usage()
            
            with self.stats_lock:
                print(f"\n📊 状态报告 [{time.strftime('%H:%M:%S')}]:")
                print(f"   下载: {self.stats['downloaded']} 个文件 ({self.stats['total_downloaded_size'] // 1024 // 1024}MB)")
                print(f"   上传: {self.stats['uploaded']} 个文件 ({self.stats['total_uploaded_size'] // 1024 // 1024}MB)")
                print(f"   跳过: {self.stats['skipped']} 个文件")
                print(f"   失败: {self.stats['failed']} 个文件")
                print(f"   磁盘: {disk['percent']:.1f}% 使用 ({disk['free'] // 1024 // 1024 // 1024:.1f}GB 可用)")
                print(f"   队列: 下载 {self.download_queue.qsize()}, 上传 {self.upload_queue.qsize()}")
                print("-" * 60)

    def run(self):
        """运行主程序"""
        print("🎯 启动 Sleep Data Manager (认证版)")
        
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
        print(f"📥 下载队列: {download_tasks} 个任务")
        print(f"📤 上传队列: {upload_tasks} 个任务")
        
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
                print(f"   跳过: {self.stats['skipped']} 个文件")
                print(f"   失败: {self.stats['failed']} 个文件")
                print(f"   总下载: {self.stats['total_downloaded_size'] // 1024 // 1024 // 1024:.2f}GB")
                print(f"   总上传: {self.stats['total_uploaded_size'] // 1024 // 1024 // 1024:.2f}GB")
        
        except KeyboardInterrupt:
            print("\n⏹️  用户中断，正在安全退出...")
        
        except Exception as e:
            print(f"\n❌ 程序错误: {e}")

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 Sleep Data 自动化管理器 - 认证版")
    print("   功能: 并行下载(带认证) + 自动上传 + 状态管理")
    print("   认证: PhysioNet + Dropbox")
    print("   作者: AI Assistant")
    print("=" * 70)
    
    manager = SleepDataManagerAuth()
    manager.run()

if __name__ == "__main__":
    main() 