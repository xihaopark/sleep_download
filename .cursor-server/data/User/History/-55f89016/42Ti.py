#!/usr/bin/env python3
"""
Sleep Data 自动上传管理器
功能：
1. 自动上传完整文件到Dropbox
2. 删除本地文件释放空间
3. 跟踪上传状态
4. 支持大文件分块上传
"""

import os
import requests
import json
import time
import sys

class SleepDataUploader:
    def __init__(self, token, download_dir="download"):
        self.token = token
        self.download_dir = download_dir
        self.uploaded_log = "uploaded_files.txt"
        
    def chunked_upload(self, file_path, dropbox_path, chunk_size=100*1024*1024):
        """分块上传大文件到Dropbox"""
        try:
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            print(f'上传: {filename} ({file_size//1024//1024}MB)')
            
            with open(file_path, 'rb') as f:
                # 开始上传会话
                start_response = requests.post(
                    'https://content.dropboxapi.com/2/files/upload_session/start',
                    headers={
                        'Authorization': f'Bearer {self.token}',
                        'Dropbox-API-Arg': json.dumps({}),
                        'Content-Type': 'application/octet-stream'
                    },
                    data=f.read(chunk_size)
                )
                
                if start_response.status_code != 200:
                    print(f'✗ 开始上传失败: {start_response.status_code}')
                    return False
                
                session_id = start_response.json()['session_id']
                offset = chunk_size
                
                # 上传剩余块
                while offset < file_size:
                    remaining = file_size - offset
                    current_chunk_size = min(chunk_size, remaining)
                    chunk_data = f.read(current_chunk_size)
                    
                    if offset + current_chunk_size < file_size:
                        # 中间块
                        append_response = requests.post(
                            'https://content.dropboxapi.com/2/files/upload_session/append_v2',
                            headers={
                                'Authorization': f'Bearer {self.token}',
                                'Dropbox-API-Arg': json.dumps({
                                    'cursor': {'session_id': session_id, 'offset': offset}
                                }),
                                'Content-Type': 'application/octet-stream'
                            },
                            data=chunk_data
                        )
                        if append_response.status_code != 200:
                            print(f'✗ 块上传失败: {append_response.status_code}')
                            return False
                    else:
                        # 最后一块
                        finish_response = requests.post(
                            'https://content.dropboxapi.com/2/files/upload_session/finish',
                            headers={
                                'Authorization': f'Bearer {self.token}',
                                'Dropbox-API-Arg': json.dumps({
                                    'cursor': {'session_id': session_id, 'offset': offset},
                                    'commit': {'path': dropbox_path, 'mode': 'add', 'autorename': True}
                                }),
                                'Content-Type': 'application/octet-stream'
                            },
                            data=chunk_data
                        )
                        if finish_response.status_code == 200:
                            print(f'✓ 上传完成: {filename}')
                            return True
                        else:
                            print(f'✗ 完成上传失败: {finish_response.status_code}')
                            return False
                    
                    offset += current_chunk_size
                    time.sleep(0.5)  # 避免API限制
                    
        except Exception as e:
            print(f'✗ 上传出错: {e}')
            return False
    
    def log_uploaded_file(self, filename):
        """记录已上传的文件"""
        with open(self.uploaded_log, 'a') as f:
            f.write(f'{filename}\n')
    
    def get_uploadable_files(self, min_size=100000000):
        """获取可上传的文件列表"""
        files = []
        for root, dirs, filenames in os.walk(self.download_dir):
            for filename in filenames:
                if filename.endswith('.edf'):
                    file_path = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(file_path)
                        if size > min_size:
                            files.append((file_path, size))
                    except:
                        pass
        
        # 按大小排序，优先上传大文件
        files.sort(key=lambda x: x[1], reverse=True)
        return files
    
    def auto_upload_batch(self, batch_size=5):
        """自动批量上传文件"""
        files = self.get_uploadable_files()
        
        if not files:
            print('没有可上传的文件')
            return
        
        selected_files = files[:batch_size]
        print(f'准备上传 {len(selected_files)} 个文件...')
        
        uploaded_count = 0
        total_freed = 0
        
        for i, (file_path, size) in enumerate(selected_files, 1):
            filename = os.path.basename(file_path)
            dropbox_path = f'/sleep_data/{filename}'
            
            print(f'[{i}/{len(selected_files)}] 处理: {filename}')
            
            if self.chunked_upload(file_path, dropbox_path):
                try:
                    os.remove(file_path)
                    print(f'✓ 上传并删除成功，释放: {size//1024//1024}MB')
                except FileNotFoundError:
                    print(f'⚠️  文件已被删除: {filename}')
                self.log_uploaded_file(filename)
                uploaded_count += 1
                total_freed += size
            else:
                print(f'✗ 上传失败: {filename}')
            
            print(f'进度: {uploaded_count}/{len(selected_files)}, 已释放: {total_freed//1024//1024//1024:.2f}GB')
            print('-' * 50)
        
        print(f'\n批量上传完成!')
        print(f'成功上传: {uploaded_count} 个文件')
        print(f'总释放空间: {total_freed//1024//1024//1024:.2f} GB')
        
        return uploaded_count, total_freed

if __name__ == "__main__":
    try:
        # 从配置文件读取token
        from dropbox_config import DROPBOX_CONFIG
        token = DROPBOX_CONFIG['access_token']
        
        uploader = SleepDataUploader(token)
        
        # 继续上传剩余文件
        uploader.auto_upload_batch(batch_size=5)
        
    except ImportError:
        print("❌ 未找到 dropbox_config.py 配置文件")
        print("请先运行: cp sensitive_config_template.py dropbox_config.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
