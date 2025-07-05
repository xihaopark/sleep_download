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
                os.remove(file_path)
                self.log_uploaded_file(filename)
                print(f'✓ 上传并删除成功，释放: {size//1024//1024}MB')
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
    token = "sl.u.AF0ZhY-38erhzFdrLPJvKAvQL3V4tFwKeK3LFCU7CIVub5KH-lBYZJje050AZ-qDY5fTqMHdMrTQOTBph2IZPNFz2tleHtAtPUR4m16XSoSaG5vFQ1GcEySeadFY7hbtZqaYyrnxmcvT2VTR35xYo2o8xAqHIlLo3qjEe71Y0mdG80Or1g3RtPKJXkIxzO9dHqrcT_Jul3gSGuljMr6rfzNYhJUQPU_PfbbhCXXMQs_IpqYa7wawSSuXtS2SLrxmoYfPFSaAhmKIDv4N7qale0AOHdjuh5-e8p5WDwdE_JqSJCbsSZlmGl-t0O3UsxHaMGjCoqy3MpDVYR2_XOPEWheLPrbKIwao6_2KKLrxvh--5oKlgE1NG4da1EVwGSQMK7g5rYHZkg1yEnWP5fHyLU8VOT8fdC6e5FIcKIC6HnvDmwzF0MTEnxkFGU9NQW5GULvDBTI8CFXRhg9sAK6StvwCft_uEtbpe1Piu3sG_AVd12G7R_wJggInGRWyN3SQBoGK5Lmtey5YWhTPvBXw-aqE37XYFJuC3VQl06cbVOIdrMi33YhdeoMiB3eLBCUt6H2Te619LzG_b6jixmH1nHmvyVcp4vGHUbNd8b_R8ffd2VooeX8UyDUAGZiYbSn4czgNGLoiPa_g7NG3RCeKz1JevcTbnQd_ynFhSs2eYonkIosSDy8XGuwXuLKvqPkH77NTerLNx8ogzk-Dy-a_E4XbZSSf9GrMGVOqr2NKk2yAmUoK6E4pZ_T6ZFAP6UKhJQJd0YPEHHD5sDY-2uJJccWlzVkN62qY_Z6GNVB94raiQEkxPSCea4Pcd9SxdKSmedEbXtCffKPYqp2BgEWpwfI_VcYegzO4dmu-35GwArPIWRmdHRG_WcYr9zUMo1gKapiHDDRutEY8BAgtN9BUs17an9dI20fSaKexBC4c7TQ-TxxpqOPsDOXgrKLZQrB7CXplfnlJZwb7L8LWS8LrIqmLhPp8F-WfiQSAGm-qdGCAmVmFqk_FeBGp9CTbe5dVx256JX-Bg56Napz15BohD6cZCoTlv5PpPBrHCx_tRYysd3MF4NYTuu5Zpnsjg5C9WetPGB_W1GLfh4QKPB70OCXRhCPM290VRn5rotm0t7c3_DFxI6fodsZ8R18xfFSnN7yg-hn9-iEHvb69K2havWfp4KQY_MCXBE8BnDFVvN6C5wNsuOnzu0MJUP4vdwhRYc54ZOeJjxtanaOcWXGlWhq9uoFhSqRM1cdjoTUxTTEqZG799fgPfFj-JNNjJHEQe-j-iZGOMYAm8ZCp8MU97V99-gXguu6kUMAYpAUUVpMumg"
    
    uploader = SleepDataUploader(token)
    
    # 继续上传剩余文件
    uploader.auto_upload_batch(batch_size=5)
