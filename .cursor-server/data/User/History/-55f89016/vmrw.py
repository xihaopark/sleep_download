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
    # 使用你的令牌
    token = "sl.u.AF34PeTlpglqeAYwABIYfeD3-SyW3tTUqkcjG_o5ffO0YJ9nT_G2pd1wHYFRqqv7z0-LFZ6jg6soFpe3KCUNDqulVlMPIWG-Mf80Jvbw72x6S9NJV-5-0IbRcXFeG7ktJWGjMFs5ynvdoFkJtzAZ9cMS3nvKk9Poqg-APtUA7IciNIDS3xa17WBDpBMg33z4Qm2FRaVgcNtu9OZ23zS7s0aNxX-SaKcWtElePah0seAESpGhHgtKTmnSOK3pt0gs5W0PqcmPw8p0y_euTs6_BGkQvieK_WdCzaOVP8Cs0dl1ep7IIYilmlEHw1HoXHstC-4oQJsIf7UFBaPNufbushoXDPftGh7wsFiW2x2c62fKDk1PtKh5B2MW2k1ZcMMK6QHom9bdFtagQ9mFSZV85stQkmNgXY2fMGaKbiMSLaNsv0BKYijWT6SEbQHAZSai6yMNn2rfWkVu_WjvaQrqTVme0WCtvNq_vhtkidxvLGQ1zDVqz-7b_JVhAGgg8gdzUk0DUUHq-HRKsg9WIgXmnn28j6exYVYqBxPxdAkL_m953kWKZKSIqcERKkjd-z7OP6VV-gdP0abDHFg8KnhZNJJufC_MG0Va1e_m4FAzMGVmNWO5Io9abHOrvDc2RyHyegVc-KZoeLZCwcov1JOhad1sPuJwvCTKDNqTNLhfLArlYYgbAygRhEI0VWNYDUnEgwov3cCcFqAPKWhGrcCQvdphhDy0AXht6-_DSqR1H36OrNfOkyypxTJzWLJ_GMh7U0M58grI0lpW5ecA0PcIy0U6Vze_Io29c8V4lZhNSSibtUevKyUa_Cg6-ay-xBiCBSPhbnc840-n-jPiK0manr55ruct-_tsFMuBtoa5S4UvDVdhuq2iT770DBmeriJDWrtfKdnc7ZxKUk_Wh18kMFyM995igTxyLuejytQhAUhbuWiMlTHik01m2382_H_yOwwpZ-wU0-EXp7_VatSEPJWPSAO3MJgCuc8y8Fdnk10MY6BzKc3EpbIbJtnIzTsxLiLu2aWklgzwuGkt_HsolNKgKTYEpqYvdT8gWZBBKUl9p9ETqP_lEkGfQ6j1RdXsSvtMiWJGl7xje6g5cwLfuwwXdMyly_PugCxdySaiuLQACguUpvk-M52P9Pgigu3cKxbuviy7mhT-bWdGLOo1FLqnHNTYkdY45-aMjL5JNL2i_ZdKNTgNuvseNd4C-uegmY6qXrpnOMO2uSxHe-p9JI2Sy9qo2_K-PWU5Bpp-3IQ6MsuVuSoC_IOWbpWtn9kG6g92FxNq9OyiVLNB6XZ-ozgeilEaelnkSs9lHk3dSt_dWw"
    
    uploader = SleepDataUploader(token)
    
    # 继续上传剩余文件
    uploader.auto_upload_batch(batch_size=5)
