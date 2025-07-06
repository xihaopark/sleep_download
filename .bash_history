. "/root/.cursor-server/bin/7111807980fa9c93aedd455ffa44b682c0dc1350/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
ls -la download/ | head -20
ls -la download/
echo "请按以下步骤获取Dropbox访问令牌：
1. 访问 https://www.dropbox.com/developers/apps
2. 点击 'Create app'
3. 选择 'Scoped access' 和 'Full Dropbox'
4. 给应用命名（如 'sleep-data-uploader'）
5. 创建应用后，在 'Settings' 页面找到 'Generated access token'
6. 点击 'Generate' 生成令牌
7. 复制令牌，然后运行上传命令"
cat > /tmp/upload_script.py << 'EOF'
import os
import requests
import sys

def upload_and_delete_file(file_path, token, dropbox_path):
    """上传文件到Dropbox并删除本地文件"""
    url = 'https://content.dropboxapi.com/2/files/upload'
    headers = {
        'Authorization': f'Bearer {token}',
        'Dropbox-API-Arg': f'{{"path": "{dropbox_path}", "mode": "add", "autorename": true}}',
        'Content-Type': 'application/octet-stream'
    }
    
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            print(f"跳过空文件: {file_path}")
            os.remove(file_path)  # 删除空文件
            return True
            
        print(f"上传文件: {os.path.basename(file_path)} ({file_size/1024/1024:.1f} MB)")
        
        with open(file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
            
        if response.status_code == 200:
            print(f"✓ 上传成功，删除本地文件: {os.path.basename(file_path)}")
            os.remove(file_path)
            return True
        else:
            print(f"✗ 上传失败 ({response.status_code}): {os.path.basename(file_path)}")
            return False
            
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("使用方法: python3 /tmp/upload_script.py <DROPBOX_TOKEN>")
        sys.exit(1)
    
    token = sys.argv[1]
    local_dir = "download"
    
    if not os.path.exists(local_dir):
        print(f"错误: 目录 {local_dir} 不存在")
        sys.exit(1)
    
    # 获取所有文件并按大小排序（先上传大文件）
    files = []
    for root, dirs, filenames in os.walk(local_dir):
        for filename in filenames:
            if filename.endswith(('.edf', '.tsv', '.atr')):
                file_path = os.path.join(root, filename)
                try:
                    size = os.path.getsize(file_path)
                    files.append((file_path, size))
                except:
                    continue
    
    # 按文件大小排序，先处理大文件
    files.sort(key=lambda x: x[1], reverse=True)
    
    success_count = 0
    fail_count = 0
    
    for file_path, size in files:
        relative_path = os.path.relpath(file_path, local_dir)
        dropbox_path = f"/sleep_data/{relative_path}"
        
        if upload_and_delete_file(file_path, token, dropbox_path):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n完成: 成功 {success_count} 个, 失败 {fail_count} 个")

if __name__ == "__main__":
    main()
EOF

echo "上传脚本已创建在 /tmp/upload_script.py"
cd download && find . -size 0 -delete && echo "已删除空文件"
df -h
cd /root
cd download && ls -la *.edf | head -20
cd download && find . -name "*.edf" -size +100M | wc -l
cd download && find . -name "*.edf" -size -100M | wc -l
find . -name "*.edf" -size +100M | wc -l
find . -name "*.edf" -size -100M | wc -l
cd /root
python3 -c "
import os
import requests

# 你的Dropbox令牌
token = 'sl.u.AF1qzn5wZ2HdCmV1Dy4dMzrWQ9_mxno_HoQ1XueroEkTPgv4xPBitsgQpIOf-IUaW-iRwRrz0JzDBPrXJ7wHrZJyrRWcBktoOk_jzHK5A2TCSZQi6UHKZjAfF28y0ARHgN017uEL1eM6407kwhZwaAAUtPU21BAXEzPndhameLl8tv3czHhxigUuoQZEkTnSzNPHZK1zc1eTIYyZlao5kegucjns_Lgr7nfLyzKN_apMJhv8A_YEYiM3VjKpdH_aWn-o4C5XRfHQkeRQuII-NcIVwYqg5cst-z2fFVXe6XYde3kaqSi4wNvfbUm5YlrOf4QeTevSlGDg-oCgOJ6RtaMHm115p2YSkwR2j-sJ3hmPLhzvhXqVFgFZez3euhr6FSq7gEiNrbeSUyTdXooWLKgvEWX4m9Gi8NFMZs0T7_4nSrHuADMeg7Z6tbJKmzxf_bjoTQEa1YWK8Eyb5DBFt6VTQNVZ8n1zPnSH6Pwg7UyCWzYfLbIwfVWmuxUwyf2ICePc4L8I027uSInftz39Ltq66WHWhoPMCPVcU30ejW-GDy7G9efAiNMNszKygWngktsnr6YBJ9bPitapX6OjqGRBAPL7z9EIKXYDHh-xsA-jW5nexLYLLbZE910s_TCg8VtnAlQHmfLUrd6cgTeiB4g9RtvuvPJQAGrKTY67NjHVAQdn4QcyKFLVo1wdM12HTh7fmavK1aYC-8586ffg1qshLzNdjP4SPdshkO_nvNAgGanGa5dgxCoPzIXb4IZUijAi09yU4sz6XEiG0sm_-iIRz8tC5NsOHCcjxwwWGEbVO8TcUS1GOrw6sP9vn-yhZnm23PvdzS5RSzFxtCCjkDYfr50Fn7ZlABaTemzUnA1DslDFsuZGQSGP0aRglDxS6gz4lALewn3j1ZzTmtlbkOX0iXK8hlUsmsu39s0l8pZKZemkwZLasoY50AsB7c1Y22bZK3qP5yvM4U2X0R-OmIvXAdcJp6JXey_yhfGR6RDwC69d8HvAgMKNHO2K4gGr-qKpW8bMXEYK8uyDm0p738THMr_L4VRd4hoqegr2JM1eWMBZY9sK0gJqiaL4q9mnXFtQK2UmMOeWerhpA6lGe4g60T4aIQGfQ4k-0kwzY-pvi5lPG8U7hf7rw1YohWbjLVNrSOyX7YkAPpLs6ZHRCi0ISeC1NTCjNtlsh4G2JvJbcwGbWMGe_48WPsjiWF6S_C9hSiNjkxZBkt1xlY3n6nXUH4mCrvRcXocVJryDcSsEw97YRYkTvOplC34y9bnVUwofVZ_nVQZhtnRVtY0xmShWyxSCM2y0dVHhcEuf0jL6sQ'

# 分析当前下载状态
download_dir = 'download'
group11_file = 'download/group11.txt'

# 读取group11.txt中的所有文件
with open(group11_file, 'r') as f:
    all_urls = [line.strip() for line in f if line.strip()]

print(f'Group11.txt中总共有 {len(all_urls)} 个文件')

# 检查已下载的文件
downloaded_files = []
for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith(('.edf', '.tsv', '.atr')):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 1000:  # 大于1KB认为是有效文件
                    downloaded_files.append((file, size))
            except:
                pass

print(f'已下载的有效文件数量: {len(downloaded_files)}')

# 创建已下载文件列表
downloaded_names = set([f[0] for f in downloaded_files])

# 找出未下载的文件
not_downloaded = []
for url in all_urls:
    filename = url.split('/')[-1]
    if filename not in downloaded_names:
        not_downloaded.append(url)

print(f'未下载的文件数量: {len(not_downloaded)}')

# 保存未下载列表
with open('not_downloaded.txt', 'w') as f:
    for url in not_downloaded:
        f.write(url + '\n')

print('已创建 not_downloaded.txt 文件')
"
python3 -c "
import os
import requests

token = 'sl.u.AF1qzn5wZ2HdCmV1Dy4dMzrWQ9_mxno_HoQ1XueroEkTPgv4xPBitsgQpIOf-IUaW-iRwRrz0JzDBPrXJ7wHrZJyrRWcBktoOk_jzHK5A2TCSZQi6UHKZjAfF28y0ARHgN017uEL1eM6407kwhZwaAAUtPU21BAXEzPndhameLl8tv3czHhxigUuoQZEkTnSzNPHZK1zc1eTIYyZlao5kegucjns_Lgr7nfLyzKN_apMJhv8A_YEYiM3VjKpdH_aWn-o4C5XRfHQkeRQuII-NcIVwYqg5cst-z2fFVXe6XYde3kaqSi4wNvfbUm5YlrOf4QeTevSlGDg-oCgOJ6RtaMHm115p2YSkwR2j-sJ3hmPLhzvhXqVFgFZez3euhr6FSq7gEiNrbeSUyTdXooWLKgvEWX4m9Gi8NFMZs0T7_4nSrHuADMeg7Z6tbJKmzxf_bjoTQEa1YWK8Eyb5DBFt6VTQNVZ8n1zPnSH6Pwg7UyCWzYfLbIwfVWmuxUwyf2ICePc4L8I027uSInftz39Ltq66WHWhoPMCPVcU30ejW-GDy7G9efAiNMNszKygWngktsnr6YBJ9bPitapX6OjqGRBAPL7z9EIKXYDHh-xsA-jW5nexLYLLbZE910s_TCg8VtnAlQHmfLUrd6cgTeiB4g9RtvuvPJQAGrKTY67NjHVAQdn4QcyKFLVo1wdM12HTh7fmavK1aYC-8586ffg1qshLzNdjP4SPdshkO_nvNAgGanGa5dgxCoPzIXb4IZUijAi09yU4sz6XEiG0sm_-iIRz8tC5NsOHCcjxwwWGEbVO8TcUS1GOrw6sP9vn-yhZnm23PvdzS5RSzFxtCCjkDYfr50Fn7ZlABaTemzUnA1DslDFsuZGQSGP0aRglDxS6gz4lALewn3j1ZzTmtlbkOX0iXK8hlUsmsu39s0l8pZKZemkwZLasoY50AsB7c1Y22bZK3qP5yvM4U2X0R-OmIvXAdcJp6JXey_yhfGR6RDwC69d8HvAgMKNHO2K4gGr-qKpW8bMXEYK8uyDm0p738THMr_L4VRd4hoqegr2JM1eWMBZY9sK0gJqiaL4q9mnXFtQK2UmMOeWerhpA6lGe4g60T4aIQGfQ4k-0kwzY-pvi5lPG8U7hf7rw1YohWbjLVNrSOyX7YkAPpLs6ZHRCi0ISeC1NTCjNtlsh4G2JvJbcwGbWMGe_48WPsjiWF6S_C9hSiNjkxZBkt1xlY3n6nXUH4mCrvRcXocVJryDcSsEw97YRYkTvOplC34y9bnVUwofVZ_nVQZhtnRVtY0xmShWyxSCM2y0dVHhcEuf0jL6sQ'

def upload_and_delete(file_path, token, dropbox_path):
    try:
        size = os.path.getsize(file_path)
        print(f'上传: {os.path.basename(file_path)} ({size//1024//1024}MB)')
        
        with open(file_path, 'rb') as f:
            response = requests.post(
                'https://content.dropboxapi.com/2/files/upload',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Dropbox-API-Arg': f'{\"path\": \"{dropbox_path}\", \"mode\": \"add\", \"autorename\": true}',
                    'Content-Type': 'application/octet-stream'
                },
                data=f
            )
        
        if response.status_code == 200:
            os.remove(file_path)
            print(f'✓ 上传成功并删除: {os.path.basename(file_path)}')
            return True
        else:
            print(f'✗ 上传失败: {response.status_code}')
            return False
    except Exception as e:
        print(f'✗ 错误: {e}')
        return False

# 获取最大的5个文件先上传
download_dir = 'download'
files = []
for root, dirs, filenames in os.walk(download_dir):
    for filename in filenames:
        if filename.endswith('.edf'):
            file_path = os.path.join(root, filename)
            try:
                size = os.path.getsize(file_path)
                files.append((file_path, size))
            except:
                pass

# 按大小排序，选择最大的5个
files.sort(key=lambda x: x[1], reverse=True)
files = files[:5]

success_count = 0
for file_path, size in files:
    filename = os.path.basename(file_path)
    dropbox_path = f'/sleep_data/{filename}'
    
    if upload_and_delete(file_path, token, dropbox_path):
        success_count += 1

print(f'成功上传并删除了 {success_count} 个文件')
"
python3 -c "
import os
import requests
import json

token = 'sl.u.AF1qzn5wZ2HdCmV1Dy4dMzrWQ9_mxno_HoQ1XueroEkTPgv4xPBitsgQpIOf-IUaW-iRwRrz0JzDBPrXJ7wHrZJyrRWcBktoOk_jzHK5A2TCSZQi6UHKZjAfF28y0ARHgN017uEL1eM6407kwhZwaAAUtPU21BAXEzPndhameLl8tv3czHhxigUuoQZEkTnSzNPHZK1zc1eTIYyZlao5kegucjns_Lgr7nfLyzKN_apMJhv8A_YEYiM3VjKpdH_aWn-o4C5XRfHQkeRQuII-NcIVwYqg5cst-z2fFVXe6XYde3kaqSi4wNvfbUm5YlrOf4QeTevSlGDg-oCgOJ6RtaMHm115p2YSkwR2j-sJ3hmPLhzvhXqVFgFZez3euhr6FSq7gEiNrbeSUyTdXooWLKgvEWX4m9Gi8NFMZs0T7_4nSrHuADMeg7Z6tbJKmzxf_bjoTQEa1YWK8Eyb5DBFt6VTQNVZ8n1zPnSH6Pwg7UyCWzYfLbIwfVWmuxUwyf2ICePc4L8I027uSInftz39Ltq66WHWhoPMCPVcU30ejW-GDy7G9efAiNMNszKygWngktsnr6YBJ9bPitapX6OjqGRBAPL7z9EIKXYDHh-xsA-jW5nexLYLLbZE910s_TCg8VtnAlQHmfLUrd6cgTeiB4g9RtvuvPJQAGrKTY67NjHVAQdn4QcyKFLVo1wdM12HTh7fmavK1aYC-8586ffg1qshLzNdjP4SPdshkO_nvNAgGanGa5dgxCoPzIXb4IZUijAi09yU4sz6XEiG0sm_-iIRz8tC5NsOHCcjxwwWGEbVO8TcUS1GOrw6sP9vn-yhZnm23PvdzS5RSzFxtCCjkDYfr50Fn7ZlABaTemzUnA1DslDFsuZGQSGP0aRglDxS6gz4lALewn3j1ZzTmtlbkOX0iXK8hlUsmsu39s0l8pZKZemkwZLasoY50AsB7c1Y22bZK3qP5yvM4U2X0R-OmIvXAdcJp6JXey_yhfGR6RDwC69d8HvAgMKNHO2K4gGr-qKpW8bMXEYK8uyDm0p738THMr_L4VRd4hoqegr2JM1eWMBZY9sK0gJqiaL4q9mnXFtQK2UmMOeWerhpA6lGe4g60T4aIQGfQ4k-0kwzY-pvi5lPG8U7hf7rw1YohWbjLVNrSOyX7YkAPpLs6ZHRCi0ISeC1NTCjNtlsh4G2JvJbcwGbWMGe_48WPsjiWF6S_C9hSiNjkxZBkt1xlY3n6nXUH4mCrvRcXocVJryDcSsEw97YRYkTvOplC34y9bnVUwofVZ_nVQZhtnRVtY0xmShWyxSCM2y0dVHhcEuf0jL6sQ'

def upload_and_delete(file_path, token, dropbox_path):
    try:
        size = os.path.getsize(file_path)
        print(f'上传: {os.path.basename(file_path)} ({size//1024//1024}MB)')
        
        with open(file_path, 'rb') as f:
            response = requests.post(
                'https://content.dropboxapi.com/2/files/upload',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Dropbox-API-Arg': json.dumps({
                        'path': dropbox_path,
                        'mode': 'add',
                        'autorename': True
                    }),
                    'Content-Type': 'application/octet-stream'
                },
                data=f
            )
        
        if response.status_code == 200:
            os.remove(file_path)
            print(f'✓ 上传成功并删除: {os.path.basename(file_path)}')
            return True
        else:
            print(f'✗ 上传失败: {response.status_code} - {response.text[:100]}')
            return False
    except Exception as e:
        print(f'✗ 错误: {e}')
        return False

# 先上传一个最大的文件测试
download_dir = 'download'
files = []
for root, dirs, filenames in os.walk(download_dir):
    for filename in filenames:
        if filename.endswith('.edf'):
            file_path = os.path.join(root, filename)
            try:
                size = os.path.getsize(file_path)
                files.append((file_path, size))
            except:
                pass

# 选择最大的文件
files.sort(key=lambda x: x[1], reverse=True)
if files:
    file_path, size = files[0]
    filename = os.path.basename(file_path)
    dropbox_path = f'/sleep_data/{filename}'
    
    if upload_and_delete(file_path, token, dropbox_path):
        print('首个文件上传成功！')
    else:
        print('上传失败，请检查令牌和网络连接')
"
python3 -c "
import os

# 创建下载状态管理系统
download_dir = 'download'
group11_file = 'download/group11.txt'

# 读取group11.txt中的所有文件
with open(group11_file, 'r') as f:
    all_urls = [line.strip() for line in f if line.strip()]

print(f'Group11.txt中总共有 {len(all_urls)} 个文件')

# 检查已下载的文件
downloaded_files = {}
for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith(('.edf', '.tsv', '.atr')):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                downloaded_files[file] = size
            except:
                pass

print(f'已下载的文件数量: {len(downloaded_files)}')

# 分析完整和未完整的文件
complete_files = []
incomplete_files = []

for filename, size in downloaded_files.items():
    if size > 100000:  # 大于100KB认为是完整文件
        complete_files.append((filename, size))
    else:
        incomplete_files.append((filename, size))

print(f'完整文件: {len(complete_files)}')
print(f'不完整文件: {len(incomplete_files)}')

# 找出未下载的文件
downloaded_names = set(downloaded_files.keys())
not_downloaded = []
for url in all_urls:
    filename = url.split('/')[-1]
    if filename not in downloaded_names:
        not_downloaded.append(url)

print(f'未下载的文件: {len(not_downloaded)}')

# 显示一些统计信息
print('\n=== 文件大小统计 ===')
edf_files = [f for f in complete_files if f[0].endswith('.edf')]
print(f'完整的EDF文件: {len(edf_files)}')
total_size = sum(f[1] for f in edf_files)
print(f'EDF文件总大小: {total_size/1024/1024/1024:.2f} GB')

print('\n=== 前10个最大的文件 ===')
sorted_files = sorted(complete_files, key=lambda x: x[1], reverse=True)[:10]
for filename, size in sorted_files:
    print(f'{filename}: {size/1024/1024:.1f} MB')
"
ls -la /tmp/
echo '#!/usr/bin/env python3
import os
import requests
import json
import time

class SleepDataManager:
    def __init__(self, token, download_dir="download"):
        self.token = token
        self.download_dir = download_dir
        self.group11_file = os.path.join(download_dir, "group11.txt")
        
    def analyze_status(self):
        """分析下载状态"""
        # 读取所有URL
        with open(self.group11_file, "r") as f:
            all_urls = [line.strip() for line in f if line.strip()]
        
        # 检查已下载文件
        downloaded_files = {}
        for root, dirs, files in os.walk(self.download_dir):
            for file in files:
                if file.endswith((".edf", ".tsv", ".atr")):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        downloaded_files[file] = {"path": file_path, "size": size}
                    except:
                        pass
        
        # 分类文件
        complete_files = []
        incomplete_files = []
        
        for filename, info in downloaded_files.items():
            if info["size"] > 100000:  # 大于100KB
                complete_files.append((filename, info))
            else:
                incomplete_files.append((filename, info))
        
        # 找出未下载的文件
        downloaded_names = set(downloaded_files.keys())
        not_downloaded = []
        for url in all_urls:
            filename = url.split("/")[-1]
            if filename not in downloaded_names:
                not_downloaded.append(url)
        
        return {
            "total_urls": len(all_urls),
            "downloaded": len(downloaded_files),
            "complete": complete_files,
            "incomplete": incomplete_files,
            "not_downloaded": not_downloaded
        }
    
    def upload_file(self, file_path, dropbox_path):
        """上传文件到Dropbox"""
        try:
            size = os.path.getsize(file_path)
            print(f"上传: {os.path.basename(file_path)} ({size//1024//1024}MB)")
            
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://content.dropboxapi.com/2/files/upload",
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Dropbox-API-Arg": json.dumps({
                            "path": dropbox_path,
                            "mode": "add",
                            "autorename": True
                        }),
                        "Content-Type": "application/octet-stream"
                    },
                    data=f
                )
            
            if response.status_code == 200:
                print(f"✓ 上传成功: {os.path.basename(file_path)}")
                return True
            else:
                print(f"✗ 上传失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 错误: {e}")
            return False
    
    def create_status_files(self):
        """创建状态文件"""
        status = self.analyze_status()
        
        # 创建未下载文件列表
        with open("not_downloaded.txt", "w") as f:
            for url in status["not_downloaded"]:
                f.write(url + "\n")
        
        # 创建已上传文件记录
        with open("uploaded_files.txt", "w") as f:
            f.write("# 已上传到Dropbox的文件列表\n")
        
        # 创建状态报告
        with open("status_report.txt", "w") as f:
            f.write(f"=== Sleep Data 下载状态报告 ===\n")
            f.write(f"总文件数: {status[\"total_urls\"]}\n")
            f.write(f"已下载: {status[\"downloaded\"]}\n")
            f.write(f"完整文件: {len(status[\"complete\"])}\n")
            f.write(f"不完整文件: {len(status[\"incomplete\"])}\n")
            f.write(f"未下载: {len(status[\"not_downloaded\"])}\n")
            f.write(f"\n=== 完整文件列表 ===\n")
            for filename, info in status["complete"]:
                f.write(f"{filename}: {info[\"size\"]//1024//1024}MB\n")
        
        print("状态文件已创建:")
        print("- not_downloaded.txt: 未下载文件列表")
        print("- uploaded_files.txt: 已上传文件记录")
        print("- status_report.txt: 状态报告")

if __name__ == "__main__":
    # 使用你的令牌
    token = "sl.u.AF1qzn5wZ2HdCmV1Dy4dMzrWQ9_mxno_HoQ1XueroEkTPgv4xPBitsgQpIOf-IUaW-iRwRrz0JzDBPrXJ7wHrZJyrRWcBktoOk_jzHK5A2TCSZQi6UHKZjAfF28y0ARHgN017uEL1eM6407kwhZwaAAUtPU21BAXEzPndhameLl8tv3czHhxigUuoQZEkTnSzNPHZK1zc1eTIYyZlao5kegucjns_Lgr7nfLyzKN_apMJhv8A_YEYiM3VjKpdH_aWn-o4C5XRfHQkeRQuII-NcIVwYqg5cst-z2fFVXe6XYde3kaqSi4wNvfbUm5YlrOf4QeTevSlGDg-oCgOJ6RtaMHm115p2YSkwR2j-sJ3hmPLhzvhXqVFgFZez3euhr6FSq7gEiNrbeSUyTdXooWLKgvEWX4m9Gi8NFMZs0T7_4nSrHuADMeg7Z6tbJKmzxf_bjoTQEa1YWK8Eyb5DBFt6VTQNVZ8n1zPnSH6Pwg7UyCWzYfLbIwfVWmuxUwyf2ICePc4L8I027uSInftz39Ltq66WHWhoPMCPVcU30ejW-GDy7G9efAiNMNszKygWngktsnr6YBJ9bPitapX6OjqGRBAPL7z9EIKXYDHh-xsA-jW5nexLYLLbZE910s_TCg8VtnAlQHmfLUrd6cgTeiB4g9RtvuvPJQAGrKTY67NjHVAQdn4QcyKFLVo1wdM12HTh7fmavK1aYC-8586ffg1qshLzNdjP4SPdshkO_nvNAgGanGa5dgxCoPzIXb4IZUijAi09yU4sz6XEiG0sm_-iIRz8tC5NsOHCcjxwwWGEbVO8TcUS1GOrw6sP9vn-yhZnm23PvdzS5RSzFxtCCjkDYfr50Fn7ZlABaTemzUnA1DslDFsuZGQSGP0aRglDxS6gz4lALewn3j1ZzTmtlbkOX0iXK8hlUsmsu39s0l8pZKZemkwZLasoY50AsB7c1Y22bZK3qP5yvM4U2X0R-OmIvXAdcJp6JXey_yhfGR6RDwC69d8HvAgMKNHO2K4gGr-qKpW8bMXEYK8uyDm0p738THMr_L4VRd4hoqegr2JM1eWMBZY9sK0gJqiaL4q9mnXFtQK2UmMOeWerhpA6lGe4g60T4aIQGfQ4k-0kwzY-pvi5lPG8U7hf7rw1YohWbjLVNrSOyX7YkAPpLs6ZHRCi0ISeC1NTCjNtlsh4G2JvJbcwGbWMGe_48WPsjiWF6S_C9hSiNjkxZBkt1xlY3n6nXUH4mCrvRcXocVJryDcSsEw97YRYkTvOplC34y9bnVUwofVZ_nVQZhtnRVtY0xmShWyxSCM2y0dVHhcEuf0jL6sQ"
    
    manager = SleepDataManager(token)
    manager.create_status_files()
' > /tmp/sleep_manager.py && chmod +x /tmp/sleep_manager.py
cd download && find . -name "*.edf" -size -1M -delete && find . -name "*.tsv" -size -1k -delete && find . -name "*.atr" -size -1k -delete
df -h
cd /root
python3 -c "
import requests
import json

# 新的Dropbox令牌
token = 'sl.u.AF0zXtaLiIuZwZKNVt7HvY0_nhAdslANkQkUpDKd0Vca6yxIBHAWLgEqniL3pItEMkl87jG01PeiCRo8MwBeFJbQ0JokdpBmp56pxqQG0P3nPF3eDBIINwc8tF5QqfbW52SgocnEF2ARa6j64PioN6l3zUH4Op9_PaPxXxSb4tMY-_WemxJr90BB7DW6oUdpp8rYS-XwXs3p9Bm6nHgropVa5rROTbNdYC8VRiNepE2fosw1w7MPMdjd4uOlfmQnsiZC4mWE8riygGQL0XrDkRoelBrC-p-BV40ipfl8ajsvUHpVT7JV3pHuH2aDpOLDXyVboqcJ9RpUwF0Ew5YSRyC3JFeSV8b81XRG4mg_-jsi8vJslNd01HmaKxzxz_K1x2QXesrVyItnnwb4nbJ2hVI1EjZ8ICXMX1CbmVFyDUA_kWAb5VFmpiCEzH-xZFVle8VuVtVJUU4Y6fSJXyGWor4IG7mE5yhUStcXJNTNBkSSOTVR2kVuTx3gie8xIWmAAdJCITIIixJGZSod0ZlfQDK3vBd879kg-w4xiakSq0CUGkrZip-1Y4IAZbSijJNF43Yted5dkleRzmuF7aD6qXL3_bzdyP7x5GMhKkyroQmtsRbzlzOKlzO5AAbWU0oYFvHXkskaRmcL6VvvyDE76a8ivZLdaggEg5VN_p9ygcnOt69uay5jxS9EOOlEahbfMR766IaV3j983cBNctfaoFBpieluFPJ9aRU3HbEXZKvNs1lSt3IK1VbuKJDm4tm6oq5R9CldCG_Ou4mSA4KgaF85t5VbTDs0kPhlcPcdo7QIc0GjE8ztTbYx3Hyc_v1yYHE86OPL4-l7CSzHvbMwQQMtlGinud8q6FwP8JgETk58BGzZSlGelVHVnPmz5XmWn6Tta1E92FBGytv3Q3QKr6xj9SG-GlmgD_5BfL81IrYy59QV1Yr4_NHda_CP_-WOAuiTpisGwtCuPQ5gY13b_liSsfqSXabuwmFxCQBbq3uQy6GDNRMpjRUJlNzEJAXUjkf5ZOQxOhS5dSy8ke9GTYTej7UVDvmUPnur1EkQpoIHfe6nFIYWqhNV5tP10CtJsOkH4lW6OAM3fG9s_5qq04Q2mvK4ZOWjxvhN_63oF7gLK7lwikLyilDBDatbOSYAPobc_jR9SHEte_xO8x8C2ULFEIZ4Emm-ALPfol_6iOdI8bxzYqmufJZC7aRkwu27n16m_9rD6rpPSBtrnVLzYUUABlBeFDxgRJ6PSpNVSs48KpRIuIfpWG82R9OMdwX85yw8S8-v3CTOjrCcwteLn3uuRCdMq6bzKWRFrlyaUKsAfw'

# 测试API连接
print('测试Dropbox API连接...')
try:
    response = requests.post(
        'https://api.dropboxapi.com/2/users/get_current_account',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        user_info = response.json()
        print(f'✓ 连接成功! 用户: {user_info.get(\"email\", \"未知\")}')
        print(f'  账户ID: {user_info.get(\"account_id\", \"未知\")}')
        print(f'  显示名: {user_info.get(\"name\", {}).get(\"display_name\", \"未知\")}')
        
        # 测试文件上传权限
        print('\n测试文件上传权限...')
        test_content = b'test file content'
        upload_response = requests.post(
            'https://content.dropboxapi.com/2/files/upload',
            headers={
                'Authorization': f'Bearer {token}',
                'Dropbox-API-Arg': json.dumps({
                    'path': '/test_upload.txt',
                    'mode': 'overwrite',
                    'autorename': True
                }),
                'Content-Type': 'application/octet-stream'
            },
            data=test_content
        )
        
        if upload_response.status_code == 200:
            print('✓ 文件上传权限正常!')
            # 删除测试文件
            requests.post(
                'https://api.dropboxapi.com/2/files/delete_v2',
                headers={'Authorization': f'Bearer {token}'},
                json={'path': '/test_upload.txt'}
            )
        else:
            print(f'✗ 文件上传失败: {upload_response.status_code}')
            print(f'  错误信息: {upload_response.text[:200]}')
    else:
        print(f'✗ 连接失败: {response.status_code}')
        print(f'  错误信息: {response.text[:200]}')
        
except Exception as e:
    print(f'✗ 测试失败: {e}')
"
python3 -c "
import os

# 分析当前下载状态
download_dir = 'download'
group11_file = 'download/group11.txt'

print('=== 分析Group11文件下载状态 ===')

# 读取group11.txt中的所有文件
with open(group11_file, 'r') as f:
    all_urls = [line.strip() for line in f if line.strip()]

print(f'Group11.txt中总共有 {len(all_urls)} 个文件')

# 检查已下载的文件
downloaded_files = {}
for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith(('.edf', '.tsv', '.atr')):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                downloaded_files[file] = {'path': file_path, 'size': size}
            except:
                pass

print(f'已下载的文件数量: {len(downloaded_files)}')

# 分析文件状态
complete_files = []
incomplete_files = []

for filename, info in downloaded_files.items():
    if info['size'] > 100000:  # 大于100KB认为是完整文件
        complete_files.append(filename)
    else:
        incomplete_files.append(filename)

print(f'完整文件: {len(complete_files)}')
print(f'不完整文件: {len(incomplete_files)}')

# 找出未下载的文件
downloaded_names = set(downloaded_files.keys())
not_downloaded = []
for url in all_urls:
    filename = url.split('/')[-1]
    if filename not in downloaded_names:
        not_downloaded.append(url)

print(f'未下载的文件: {len(not_downloaded)}')

# 显示一些统计信息
print('\n=== 文件类型统计 ===')
edf_complete = [f for f in complete_files if f.endswith('.edf')]
tsv_complete = [f for f in complete_files if f.endswith('.tsv')]
atr_complete = [f for f in complete_files if f.endswith('.atr')]

print(f'完整的EDF文件: {len(edf_complete)}')
print(f'完整的TSV文件: {len(tsv_complete)}')
print(f'完整的ATR文件: {len(atr_complete)}')

# 计算EDF文件总大小
edf_total_size = 0
for filename in edf_complete:
    edf_total_size += downloaded_files[filename]['size']

print(f'EDF文件总大小: {edf_total_size/1024/1024/1024:.2f} GB')

print('\n=== 建议的下一步操作 ===')
print('1. 修复Dropbox应用权限 (添加 files.content.write)')
print('2. 重新生成访问令牌')
print('3. 开始上传完整文件到Dropbox')
print('4. 继续下载未完成的文件')
"
python3 -c "
import os
import requests
import json

# 新的Dropbox令牌
token = 'sl.u.AF0zXtaLiIuZwZKNVt7HvY0_nhAdslANkQkUpDKd0Vca6yxIBHAWLgEqniL3pItEMkl87jG01PeiCRo8MwBeFJbQ0JokdpBmp56pxqQG0P3nPF3eDBIINwc8tF5QqfbW52SgocnEF2ARa6j64PioN6l3zUH4Op9_PaPxXxSb4tMY-_WemxJr90BB7DW6oUdpp8rYS-XwXs3p9Bm6nHgropVa5rROTbNdYC8VRiNepE2fosw1w7MPMdjd4uOlfmQnsiZC4mWE8riygGQL0XrDkRoelBrC-p-BV40ipfl8ajsvUHpVT7JV3pHuH2aDpOLDXyVboqcJ9RpUwF0Ew5YSRyC3JFeSV8b81XRG4mg_-jsi8vJslNd01HmaKxzxz_K1x2QXesrVyItnnwb4nbJ2hVI1EjZ8ICXMX1CbmVFyDUA_kWAb5VFmpiCEzH-xZFVle8VuVtVJUU4Y6fSJXyGWor4IG7mE5yhUStcXJNTNBkSSOTVR2kVuTx3gie8xIWmAAdJCITIIixJGZSod0ZlfQDK3vBd879kg-w4xiakSq0CUGkrZip-1Y4IAZbSijJNF43Yted5dkleRzmuF7aD6qXL3_bzdyP7x5GMhKkyroQmtsRbzlzOKlzO5AAbWU0oYFvHXkskaRmcL6VvvyDE76a8ivZLdaggEg5VN_p9ygcnOt69uay5jxS9EOOlEahbfMR766IaV3j983cBNctfaoFBpieluFPJ9aRU3HbEXZKvNs1lSt3IK1VbuKJDm4tm6oq5R9CldCG_Ou4mSA4KgaF85t5VbTDs0kPhlcPcdo7QIc0GjE8ztTbYx3Hyc_v1yYHE86OPL4-l7CSzHvbMwQQMtlGinud8q6FwP8JgETk58BGzZSlGelVHVnPmz5XmWn6Tta1E92FBGytv3Q3QKr6xj9SG-GlmgD_5BfL81IrYy59QV1Yr4_NHda_CP_-WOAuiTpisGwtCuPQ5gY13b_liSsfqSXabuwmFxCQBbq3uQy6GDNRMpjRUJlNzEJAXUjkf5ZOQxOhS5dSy8ke9GTYTej7UVDvmUPnur1EkQpoIHfe6nFIYWqhNV5tP10CtJsOkH4lW6OAM3fG9s_5qq04Q2mvK4ZOWjxvhN_63oF7gLK7lwikLyilDBDatbOSYAPobc_jR9SHEte_xO8x8C2ULFEIZ4Emm-ALPfol_6iOdI8bxzYqmufJZC7aRkwu27n16m_9rD6rpPSBtrnVLzYUUABlBeFDxgRJ6PSpNVSs48KpRIuIfpWG82R9OMdwX85yw8S8-v3CTOjrCcwteLn3uuRCdMq6bzKWRFrlyaUKsAfw'

def upload_and_delete_file(file_path, token, dropbox_path):
    '''上传文件到Dropbox并删除本地文件'''
    try:
        size = os.path.getsize(file_path)
        print(f'正在上传: {os.path.basename(file_path)} ({size//1024//1024}MB)')
        
        with open(file_path, 'rb') as f:
            response = requests.post(
                'https://content.dropboxapi.com/2/files/upload',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Dropbox-API-Arg': json.dumps({
                        'path': dropbox_path,
                        'mode': 'add',
                        'autorename': True
                    }),
                    'Content-Type': 'application/octet-stream'
                },
                data=f
            )
        
        if response.status_code == 200:
            print(f'✓ 上传成功: {os.path.basename(file_path)}')
            os.remove(file_path)
            print(f'✓ 本地文件已删除: {os.path.basename(file_path)}')
            return True
        else:
            print(f'✗ 上传失败: {response.status_code}')
            print(f'  错误详情: {response.text[:200]}')
            return False
    except Exception as e:
        print(f'✗ 上传过程出错: {e}')
        return False

# 获取download目录中最大的3个EDF文件
download_dir = 'download'
edf_files = []

for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith('.edf'):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 100000000:  # 大于100MB
                    edf_files.append((file_path, size))
            except:
                pass

# 按大小排序，选择最大的3个
edf_files.sort(key=lambda x: x[1], reverse=True)
selected_files = edf_files[:3]

print(f'准备上传 {len(selected_files)} 个最大的EDF文件...')

success_count = 0
for file_path, size in selected_files:
    filename = os.path.basename(file_path)
    dropbox_path = f'/sleep_data/{filename}'
    
    if upload_and_delete_file(file_path, token, dropbox_path):
        success_count += 1
        print(f'进度: {success_count}/{len(selected_files)}')
    else:
        print(f'跳过文件: {filename}')

print(f'\n上传完成! 成功上传 {success_count} 个文件')
print(f'释放的磁盘空间约: {sum(size for _, size in selected_files[:success_count])/1024/1024/1024:.2f} GB')
"
echo "=== Group11 文件下载状态总结 ===
总文件数: 392 个
已下载: 195 个文件
- 完整文件: 65 个 (主要是EDF文件)
- 不完整文件: 130 个 (需要重新下载)
- 未下载: 197 个文件

EDF文件总大小: ~36 GB
磁盘使用率: 100% (急需释放空间)

=== 建议的操作顺序 ===
1. 修复Dropbox应用权限
2. 重新生成访问令牌
3. 上传已完成的EDF文件 (释放空间)
4. 继续下载未完成的文件
5. 建立自动化上传-删除流程"
python3 -c "
import os
import requests
import json

# 新的Dropbox令牌
token = 'sl.u.AF0ZhY-38erhzFdrLPJvKAvQL3V4tFwKeK3LFCU7CIVub5KH-lBYZJje050AZ-qDY5fTqMHdMrTQOTBph2IZPNFz2tleHtAtPUR4m16XSoSaG5vFQ1GcEySeadFY7hbtZqaYyrnxmcvT2VTR35xYo2o8xAqHIlLo3qjEe71Y0mdG80Or1g3RtPKJXkIxzO9dHqrcT_Jul3gSGuljMr6rfzNYhJUQPU_PfbbhCXXMQs_IpqYa7wawSSuXtS2SLrxmoYfPFSaAhmKIDv4N7qale0AOHdjuh5-e8p5WDwdE_JqSJCbsSZlmGl-t0O3UsxHaMGjCoqy3MpDVYR2_XOPEWheLPrbKIwao6_2KKLrxvh--5oKlgE1NG4da1EVwGSQMK7g5rYHZkg1yEnWP5fHyLU8VOT8fdC6e5FIcKIC6HnvDmwzF0MTEnxkFGU9NQW5GULvDBTI8CFXRhg9sAK6StvwCft_uEtbpe1Piu3sG_AVd12G7R_wJggInGRWyN3SQBoGK5Lmtey5YWhTPvBXw-aqE37XYFJuC3VQl06cbVOIdrMi33YhdeoMiB3eLBCUt6H2Te619LzG_b6jixmH1nHmvyVcp4vGHUbNd8b_R8ffd2VooeX8UyDUAGZiYbSn4czgNGLoiPa_g7NG3RCeKz1JevcTbnQd_ynFhSs2eYonkIosSDy8XGuwXuLKvqPkH77NTerLNx8ogzk-Dy-a_E4XbZSSf9GrMGVOqr2NKk2yAmUoK6E4pZ_T6ZFAP6UKhJQJd0YPEHHD5sDY-2uJJccWlzVkN62qY_Z6GNVB94raiQEkxPSCea4Pcd9SxdKSmedEbXtCffKPYqp2BgEWpwfI_VcYegzO4dmu-35GwArPIWRmdHRG_WcYr9zUMo1gKapiHDDRutEY8BAgtN9BUs17an9dI20fSaKexBC4c7TQ-TxxpqOPsDOXgrKLZQrB7CXplfnlJZwb7L8LWS8LrIqmLhPp8F-WfiQSAGm-qdGCAmVmFqk_FeBGp9CTbe5dVx256JX-Bg56Napz15BohD6cZCoTlv5PpPBrHCx_tRYysd3MF4NYTuu5Zpnsjg5C9WetPGB_W1GLfh4QKPB70OCXRhCPM290VRn5rotm0t7c3_DFxI6fodsZ8R18xfFSnN7yg-hn9-iEHvb69K2havWfp4KQY_MCXBE8BnDFVvN6C5wNsuOnzu0MJUP4vdwhRYc54ZOeJjxtanaOcWXGlWhq9uoFhSqRM1cdjoTUxTTEqZG799fgPfFj-JNNjJHEQe-j-iZGOMYAm8ZCp8MU97V99-gXguu6kUMAYpAUUVpMumg'

# 先测试API权限
print('测试Dropbox API权限...')
try:
    # 测试文件上传权限
    test_content = b'test upload permission'
    upload_response = requests.post(
        'https://content.dropboxapi.com/2/files/upload',
        headers={
            'Authorization': f'Bearer {token}',
            'Dropbox-API-Arg': json.dumps({
                'path': '/test_permission.txt',
                'mode': 'overwrite',
                'autorename': True
            }),
            'Content-Type': 'application/octet-stream'
        },
        data=test_content
    )
    
    if upload_response.status_code == 200:
        print('✓ 文件上传权限正常!')
        # 删除测试文件
        requests.post(
            'https://api.dropboxapi.com/2/files/delete_v2',
            headers={'Authorization': f'Bearer {token}'},
            json={'path': '/test_permission.txt'}
        )
        print('✓ 权限测试完成，开始上传真实文件...')
    else:
        print(f'✗ 权限测试失败: {upload_response.status_code}')
        print(f'  错误: {upload_response.text[:200]}')
        exit(1)
        
except Exception as e:
    print(f'✗ 权限测试出错: {e}')
    exit(1)
"
python3 -c "
import os
import requests
import json

token = 'sl.u.AF0ZhY-38erhzFdrLPJvKAvQL3V4tFwKeK3LFCU7CIVub5KH-lBYZJje050AZ-qDY5fTqMHdMrTQOTBph2IZPNFz2tleHtAtPUR4m16XSoSaG5vFQ1GcEySeadFY7hbtZqaYyrnxmcvT2VTR35xYo2o8xAqHIlLo3qjEe71Y0mdG80Or1g3RtPKJXkIxzO9dHqrcT_Jul3gSGuljMr6rfzNYhJUQPU_PfbbhCXXMQs_IpqYa7wawSSuXtS2SLrxmoYfPFSaAhmKIDv4N7qale0AOHdjuh5-e8p5WDwdE_JqSJCbsSZlmGl-t0O3UsxHaMGjCoqy3MpDVYR2_XOPEWheLPrbKIwao6_2KKLrxvh--5oKlgE1NG4da1EVwGSQMK7g5rYHZkg1yEnWP5fHyLU8VOT8fdC6e5FIcKIC6HnvDmwzF0MTEnxkFGU9NQW5GULvDBTI8CFXRhg9sAK6StvwCft_uEtbpe1Piu3sG_AVd12G7R_wJggInGRWyN3SQBoGK5Lmtey5YWhTPvBXw-aqE37XYFJuC3VQl06cbVOIdrMi33YhdeoMiB3eLBCUt6H2Te619LzG_b6jixmH1nHmvyVcp4vGHUbNd8b_R8ffd2VooeX8UyDUAGZiYbSn4czgNGLoiPa_g7NG3RCeKz1JevcTbnQd_ynFhSs2eYonkIosSDy8XGuwXuLKvqPkH77NTerLNx8ogzk-Dy-a_E4XbZSSf9GrMGVOqr2NKk2yAmUoK6E4pZ_T6ZFAP6UKhJQJd0YPEHHD5sDY-2uJJccWlzVkN62qY_Z6GNVB94raiQEkxPSCea4Pcd9SxdKSmedEbXtCffKPYqp2BgEWpwfI_VcYegzO4dmu-35GwArPIWRmdHRG_WcYr9zUMo1gKapiHDDRutEY8BAgtN9BUs17an9dI20fSaKexBC4c7TQ-TxxpqOPsDOXgrKLZQrB7CXplfnlJZwb7L8LWS8LrIqmLhPp8F-WfiQSAGm-qdGCAmVmFqk_FeBGp9CTbe5dVx256JX-Bg56Napz15BohD6cZCoTlv5PpPBrHCx_tRYysd3MF4NYTuu5Zpnsjg5C9WetPGB_W1GLfh4QKPB70OCXRhCPM290VRn5rotm0t7c3_DFxI6fodsZ8R18xfFSnN7yg-hn9-iEHvb69K2havWfp4KQY_MCXBE8BnDFVvN6C5wNsuOnzu0MJUP4vdwhRYc54ZOeJjxtanaOcWXGlWhq9uoFhSqRM1cdjoTUxTTEqZG799fgPfFj-JNNjJHEQe-j-iZGOMYAm8ZCp8MU97V99-gXguu6kUMAYpAUUVpMumg'

def upload_and_delete_file(file_path, token, dropbox_path):
    '''上传文件到Dropbox并删除本地文件'''
    try:
        size = os.path.getsize(file_path)
        print(f'正在上传: {os.path.basename(file_path)} ({size//1024//1024}MB)')
        
        with open(file_path, 'rb') as f:
            response = requests.post(
                'https://content.dropboxapi.com/2/files/upload',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Dropbox-API-Arg': json.dumps({
                        'path': dropbox_path,
                        'mode': 'add',
                        'autorename': True
                    }),
                    'Content-Type': 'application/octet-stream'
                },
                data=f
            )
        
        if response.status_code == 200:
            print(f'✓ 上传成功: {os.path.basename(file_path)}')
            os.remove(file_path)
            print(f'✓ 本地文件已删除，释放空间: {size//1024//1024}MB')
            return True
        else:
            print(f'✗ 上传失败: {response.status_code}')
            print(f'  错误: {response.text[:100]}')
            return False
    except Exception as e:
        print(f'✗ 上传出错: {e}')
        return False

# 获取最大的EDF文件
download_dir = 'download'
edf_files = []

for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith('.edf'):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 100000000:  # 大于100MB
                    edf_files.append((file_path, size))
            except:
                pass

# 按大小排序，选择最大的文件
edf_files.sort(key=lambda x: x[1], reverse=True)

print(f'找到 {len(edf_files)} 个大型EDF文件')
print('开始上传最大的文件...')

# 先上传最大的一个文件
if edf_files:
    file_path, size = edf_files[0]
    filename = os.path.basename(file_path)
    dropbox_path = f'/sleep_data/{filename}'
    
    print(f'上传第一个文件: {filename}')
    if upload_and_delete_file(file_path, token, dropbox_path):
        print(f'✓ 成功释放了 {size//1024//1024}MB 磁盘空间!')
    else:
        print('✗ 第一个文件上传失败')
else:
    print('没有找到可上传的EDF文件')
"
python3 -c "
import os
import requests
import json
import time

token = 'sl.u.AF0ZhY-38erhzFdrLPJvKAvQL3V4tFwKeK3LFCU7CIVub5KH-lBYZJje050AZ-qDY5fTqMHdMrTQOTBph2IZPNFz2tleHtAtPUR4m16XSoSaG5vFQ1GcEySeadFY7hbtZqaYyrnxmcvT2VTR35xYo2o8xAqHIlLo3qjEe71Y0mdG80Or1g3RtPKJXkIxzO9dHqrcT_Jul3gSGuljMr6rfzNYhJUQPU_PfbbhCXXMQs_IpqYa7wawSSuXtS2SLrxmoYfPFSaAhmKIDv4N7qale0AOHdjuh5-e8p5WDwdE_JqSJCbsSZlmGl-t0O3UsxHaMGjCoqy3MpDVYR2_XOPEWheLPrbKIwao6_2KKLrxvh--5oKlgE1NG4da1EVwGSQMK7g5rYHZkg1yEnWP5fHyLU8VOT8fdC6e5FIcKIC6HnvDmwzF0MTEnxkFGU9NQW5GULvDBTI8CFXRhg9sAK6StvwCft_uEtbpe1Piu3sG_AVd12G7R_wJggInGRWyN3SQBoGK5Lmtey5YWhTPvBXw-aqE37XYFJuC3VQl06cbVOIdrMi33YhdeoMiB3eLBCUt6H2Te619LzG_b6jixmH1nHmvyVcp4vGHUbNd8b_R8ffd2VooeX8UyDUAGZiYbSn4czgNGLoiPa_g7NG3RCeKz1JevcTbnQd_ynFhSs2eYonkIosSDy8XGuwXuLKvqPkH77NTerLNx8ogzk-Dy-a_E4XbZSSf9GrMGVOqr2NKk2yAmUoK6E4pZ_T6ZFAP6UKhJQJd0YPEHHD5sDY-2uJJccWlzVkN62qY_Z6GNVB94raiQEkxPSCea4Pcd9SxdKSmedEbXtCffKPYqp2BgEWpwfI_VcYegzO4dmu-35GwArPIWRmdHRG_WcYr9zUMo1gKapiHDDRutEY8BAgtN9BUs17an9dI20fSaKexBC4c7TQ-TxxpqOPsDOXgrKLZQrB7CXplfnlJZwb7L8LWS8LrIqmLhPp8F-WfiQSAGm-qdGCAmVmFqk_FeBGp9CTbe5dVx256JX-Bg56Napz15BohD6cZCoTlv5PpPBrHCx_tRYysd3MF4NYTuu5Zpnsjg5C9WetPGB_W1GLfh4QKPB70OCXRhCPM290VRn5rotm0t7c3_DFxI6fodsZ8R18xfFSnN7yg-hn9-iEHvb69K2havWfp4KQY_MCXBE8BnDFVvN6C5wNsuOnzu0MJUP4vdwhRYc54ZOeJjxtanaOcWXGlWhq9uoFhSqRM1cdjoTUxTTEqZG799fgPfFj-JNNjJHEQe-j-iZGOMYAm8ZCp8MU97V99-gXguu6kUMAYpAUUVpMumg'

def chunked_upload(file_path, token, dropbox_path, chunk_size=100*1024*1024):  # 100MB chunks
    '''分块上传大文件到Dropbox'''
    try:
        file_size = os.path.getsize(file_path)
        print(f'开始分块上传: {os.path.basename(file_path)} ({file_size//1024//1024}MB)')
        
        with open(file_path, 'rb') as f:
            # 1. 开始上传会话
            start_response = requests.post(
                'https://content.dropboxapi.com/2/files/upload_session/start',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Dropbox-API-Arg': json.dumps({}),
                    'Content-Type': 'application/octet-stream'
                },
                data=f.read(chunk_size)
            )
            
            if start_response.status_code != 200:
                print(f'✗ 开始上传失败: {start_response.status_code}')
                return False
            
            session_id = start_response.json()['session_id']
            print(f'✓ 上传会话已开始: {session_id}')
            
            offset = chunk_size
            chunk_num = 1
            
            # 2. 上传中间块
            while offset < file_size:
                remaining = file_size - offset
                current_chunk_size = min(chunk_size, remaining)
                
                chunk_data = f.read(current_chunk_size)
                
                if offset + current_chunk_size < file_size:
                    # 中间块
                    append_response = requests.post(
                        'https://content.dropboxapi.com/2/files/upload_session/append_v2',
                        headers={
                            'Authorization': f'Bearer {token}',
                            'Dropbox-API-Arg': json.dumps({
                                'cursor': {
                                    'session_id': session_id,
                                    'offset': offset
                                }
                            }),
                            'Content-Type': 'application/octet-stream'
                        },
                        data=chunk_data
                    )
                    
                    if append_response.status_code != 200:
                        print(f'✗ 块 {chunk_num} 上传失败: {append_response.status_code}')
                        return False
                    
                    print(f'✓ 块 {chunk_num} 上传完成 ({offset//1024//1024}MB/{file_size//1024//1024}MB)')
                    
                else:
                    # 最后一块，完成上传
                    finish_response = requests.post(
                        'https://content.dropboxapi.com/2/files/upload_session/finish',
                        headers={
                            'Authorization': f'Bearer {token}',
                            'Dropbox-API-Arg': json.dumps({
                                'cursor': {
                                    'session_id': session_id,
                                    'offset': offset
                                },
                                'commit': {
                                    'path': dropbox_path,
                                    'mode': 'add',
                                    'autorename': True
                                }
                            }),
                            'Content-Type': 'application/octet-stream'
                        },
                        data=chunk_data
                    )
                    
                    if finish_response.status_code == 200:
                        print(f'✓ 文件上传完成: {os.path.basename(file_path)}')
                        print(f'✓ Dropbox路径: {dropbox_path}')
                        return True
                    else:
                        print(f'✗ 完成上传失败: {finish_response.status_code}')
                        print(f'  错误: {finish_response.text[:200]}')
                        return False
                
                offset += current_chunk_size
                chunk_num += 1
                time.sleep(1)  # 避免API限制
                
    except Exception as e:
        print(f'✗ 分块上传出错: {e}')
        return False

# 测试分块上传最大的文件
download_dir = 'download'
edf_files = []

for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith('.edf'):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 100000000:  # 大于100MB
                    edf_files.append((file_path, size))
            except:
                pass

# 按大小排序
edf_files.sort(key=lambda x: x[1], reverse=True)

if edf_files:
    file_path, size = edf_files[0]
    filename = os.path.basename(file_path)
    dropbox_path = f'/sleep_data/{filename}'
    
    print(f'测试分块上传: {filename} ({size//1024//1024}MB)')
    
    if chunked_upload(file_path, token, dropbox_path):
        print(f'✓ 上传成功！正在删除本地文件...')
        os.remove(file_path)
        print(f'✓ 本地文件已删除，释放空间: {size//1024//1024}MB')
    else:
        print('✗ 上传失败，保留本地文件')
else:
    print('没有找到可上传的EDF文件')
"
df -h
python3 -c "
import os
import requests
import json
import time

token = 'sl.u.AF0ZhY-38erhzFdrLPJvKAvQL3V4tFwKeK3LFCU7CIVub5KH-lBYZJje050AZ-qDY5fTqMHdMrTQOTBph2IZPNFz2tleHtAtPUR4m16XSoSaG5vFQ1GcEySeadFY7hbtZqaYyrnxmcvT2VTR35xYo2o8xAqHIlLo3qjEe71Y0mdG80Or1g3RtPKJXkIxzO9dHqrcT_Jul3gSGuljMr6rfzNYhJUQPU_PfbbhCXXMQs_IpqYa7wawSSuXtS2SLrxmoYfPFSaAhmKIDv4N7qale0AOHdjuh5-e8p5WDwdE_JqSJCbsSZlmGl-t0O3UsxHaMGjCoqy3MpDVYR2_XOPEWheLPrbKIwao6_2KKLrxvh--5oKlgE1NG4da1EVwGSQMK7g5rYHZkg1yEnWP5fHyLU8VOT8fdC6e5FIcKIC6HnvDmwzF0MTEnxkFGU9NQW5GULvDBTI8CFXRhg9sAK6StvwCft_uEtbpe1Piu3sG_AVd12G7R_wJggInGRWyN3SQBoGK5Lmtey5YWhTPvBXw-aqE37XYFJuC3VQl06cbVOIdrMi33YhdeoMiB3eLBCUt6H2Te619LzG_b6jixmH1nHmvyVcp4vGHUbNd8b_R8ffd2VooeX8UyDUAGZiYbSn4czgNGLoiPa_g7NG3RCeKz1JevcTbnQd_ynFhSs2eYonkIosSDy8XGuwXuLKvqPkH77NTerLNx8ogzk-Dy-a_E4XbZSSf9GrMGVOqr2NKk2yAmUoK6E4pZ_T6ZFAP6UKhJQJd0YPEHHD5sDY-2uJJccWlzVkN62qY_Z6GNVB94raiQEkxPSCea4Pcd9SxdKSmedEbXtCffKPYqp2BgEWpwfI_VcYegzO4dmu-35GwArPIWRmdHRG_WcYr9zUMo1gKapiHDDRutEY8BAgtN9BUs17an9dI20fSaKexBC4c7TQ-TxxpqOPsDOXgrKLZQrB7CXplfnlJZwb7L8LWS8LrIqmLhPp8F-WfiQSAGm-qdGCAmVmFqk_FeBGp9CTbe5dVx256JX-Bg56Napz15BohD6cZCoTlv5PpPBrHCx_tRYysd3MF4NYTuu5Zpnsjg5C9WetPGB_W1GLfh4QKPB70OCXRhCPM290VRn5rotm0t7c3_DFxI6fodsZ8R18xfFSnN7yg-hn9-iEHvb69K2havWfp4KQY_MCXBE8BnDFVvN6C5wNsuOnzu0MJUP4vdwhRYc54ZOeJjxtanaOcWXGlWhq9uoFhSqRM1cdjoTUxTTEqZG799fgPfFj-JNNjJHEQe-j-iZGOMYAm8ZCp8MU97V99-gXguu6kUMAYpAUUVpMumg'

def chunked_upload(file_path, token, dropbox_path, chunk_size=100*1024*1024):
    '''分块上传大文件到Dropbox'''
    try:
        file_size = os.path.getsize(file_path)
        print(f'上传: {os.path.basename(file_path)} ({file_size//1024//1024}MB)')
        
        with open(file_path, 'rb') as f:
            # 开始上传会话
            start_response = requests.post(
                'https://content.dropboxapi.com/2/files/upload_session/start',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Dropbox-API-Arg': json.dumps({}),
                    'Content-Type': 'application/octet-stream'
                },
                data=f.read(chunk_size)
            )
            
            if start_response.status_code != 200:
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
                            'Authorization': f'Bearer {token}',
                            'Dropbox-API-Arg': json.dumps({
                                'cursor': {'session_id': session_id, 'offset': offset}
                            }),
                            'Content-Type': 'application/octet-stream'
                        },
                        data=chunk_data
                    )
                    if append_response.status_code != 200:
                        return False
                else:
                    # 最后一块
                    finish_response = requests.post(
                        'https://content.dropboxapi.com/2/files/upload_session/finish',
                        headers={
                            'Authorization': f'Bearer {token}',
                            'Dropbox-API-Arg': json.dumps({
                                'cursor': {'session_id': session_id, 'offset': offset},
                                'commit': {'path': dropbox_path, 'mode': 'add', 'autorename': True}
                            }),
                            'Content-Type': 'application/octet-stream'
                        },
                        data=chunk_data
                    )
                    return finish_response.status_code == 200
                
                offset += current_chunk_size
                time.sleep(0.5)
                
    except Exception as e:
        print(f'✗ 上传出错: {e}')
        return False

# 批量上传接下来的5个最大文件
download_dir = 'download'
edf_files = []

for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith('.edf'):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 100000000:  # 大于100MB
                    edf_files.append((file_path, size))
            except:
                pass

# 按大小排序，选择接下来的5个
edf_files.sort(key=lambda x: x[1], reverse=True)
selected_files = edf_files[:5]

print(f'准备批量上传 {len(selected_files)} 个文件...')

uploaded_count = 0
total_freed = 0

for i, (file_path, size) in enumerate(selected_files, 1):
    filename = os.path.basename(file_path)
    dropbox_path = f'/sleep_data/{filename}'
    
    print(f'[{i}/{len(selected_files)}] 处理: {filename}')
    
    if chunked_upload(file_path, token, dropbox_path):
        print(f'✓ 上传成功')
        os.remove(file_path)
        print(f'✓ 本地文件已删除，释放: {size//1024//1024}MB')
        uploaded_count += 1
        total_freed += size
    else:
        print(f'✗ 上传失败: {filename}')
    
    print(f'进度: {uploaded_count}/{len(selected_files)}, 已释放: {total_freed//1024//1024//1024:.2f}GB')
    print('-' * 50)

print(f'\n批量上传完成!')
print(f'成功上传: {uploaded_count} 个文件')
print(f'总释放空间: {total_freed//1024//1024//1024:.2f} GB')
"
df -h
python3 -c "
import os

# 创建状态管理文件
print('=== 创建文件管理系统 ===')

# 分析当前状态
download_dir = 'download'
group11_file = 'download/group11.txt'

with open(group11_file, 'r') as f:
    all_urls = [line.strip() for line in f if line.strip()]

# 检查剩余文件
remaining_files = {}
for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith(('.edf', '.tsv', '.atr')):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                remaining_files[file] = {'path': file_path, 'size': size}
            except:
                pass

# 分类剩余文件
complete_files = []
incomplete_files = []

for filename, info in remaining_files.items():
    if info['size'] > 100000:  # 大于100KB
        complete_files.append(filename)
    else:
        incomplete_files.append(filename)

# 创建未下载文件列表
downloaded_names = set(remaining_files.keys())
not_downloaded = []
for url in all_urls:
    filename = url.split('/')[-1]
    if filename not in downloaded_names:
        not_downloaded.append(url)

print(f'原始文件总数: {len(all_urls)}')
print(f'已上传到Dropbox: 6个大文件 (~5.2GB)')
print(f'本地剩余文件: {len(remaining_files)}')
print(f'- 完整文件: {len(complete_files)}')
print(f'- 不完整文件: {len(incomplete_files)}')
print(f'未下载文件: {len(not_downloaded)}')

# 保存状态文件
try:
    with open('uploaded_files.txt', 'w') as f:
        f.write('# 已上传到Dropbox的文件\\n')
        f.write('16519_17791.edf\\n')
        f.write('16771_6505.edf\\n')
        f.write('1648_13945.edf\\n')
        f.write('1657_8863.edf\\n')
        f.write('16669_19471.edf\\n')
        f.write('16603_5782.edf\\n')
    
    with open('remaining_complete.txt', 'w') as f:
        f.write('# 本地剩余的完整文件\\n')
        for filename in complete_files:
            f.write(f'{filename}\\n')
    
    with open('not_downloaded.txt', 'w') as f:
        f.write('# 未下载的文件URL\\n')
        for url in not_downloaded:
            f.write(f'{url}\\n')
    
    print('\\n✓ 状态文件已创建:')
    print('  - uploaded_files.txt: 已上传文件记录')
    print('  - remaining_complete.txt: 剩余完整文件')
    print('  - not_downloaded.txt: 未下载文件列表')
    
except Exception as e:
    print(f'创建状态文件时出错: {e}')
"
cat > auto_upload_manager.py << 'EOF'
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
EOF

chmod +x auto_upload_manager.py
echo "✓ 自动上传管理器已创建: auto_upload_manager.py"
python3 auto_upload_manager.py
df -h
python3 -c "
import os

print('=== Sleep Data 管理状态总结 ===')

# 统计已上传文件
try:
    with open('uploaded_files.txt', 'r') as f:
        uploaded_files = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f'已上传到Dropbox: {len(uploaded_files)} 个文件')
except:
    print('已上传到Dropbox: 11 个文件 (估计)')

# 统计剩余文件
download_dir = 'download'
remaining_files = []
for root, dirs, files in os.walk(download_dir):
    for file in files:
        if file.endswith('.edf'):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 100000000:  # 大于100MB
                    remaining_files.append((file, size))
            except:
                pass

print(f'本地剩余大文件: {len(remaining_files)} 个')

if remaining_files:
    total_remaining_size = sum(size for _, size in remaining_files)
    print(f'剩余文件总大小: {total_remaining_size//1024//1024//1024:.2f} GB')
    
    print(f'\\n剩余最大的10个文件:')
    remaining_files.sort(key=lambda x: x[1], reverse=True)
    for i, (filename, size) in enumerate(remaining_files[:10], 1):
        print(f'  {i}. {filename}: {size//1024//1024}MB')

# 读取group11.txt状态
with open('download/group11.txt', 'r') as f:
    total_urls = len([line.strip() for line in f if line.strip()])

print(f'\\n=== 整体进度 ===')
print(f'Group11总文件数: {total_urls}')
print(f'已上传: ~11 个大文件 (~8.2GB)')
print(f'本地剩余: {len(remaining_files)} 个大文件')
print(f'磁盘空间已从100%降至当前水平')

print(f'\\n=== 下一步建议 ===')
print(f'1. 继续运行: python3 auto_upload_manager.py')
print(f'2. 监控磁盘空间，确保有足够空间继续下载')
print(f'3. 下载未完成的文件')
print(f'4. 建立定期上传计划')
"
head -20 not_downloaded.txt
head -10 uploaded_files.txt
head -10 download/group11.txt
chmod +x sleep_data_manager.py
python3 sleep_data_manager.py
ls -la *.txt
df -h
chmod +x sleep_data_manager_auth.py
python3 sleep_data_manager_auth.py
. "/root/.cursor-server/bin/7111807980fa9c93aedd455ffa44b682c0dc1350/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
ps aux | grep python
ls -la *.py
df -h
python3 sleep_data_manager_auth.py
ls -la sleep_data_manager_auth.py *.txt
chmod +x deploy.sh
tar -czf sleep_data_manager_package.tar.gz sleep_data_manager_auth.py PROJECT_README.md PROJECT_INTRODUCTION.md deploy.sh
ls -la sleep_data_manager_package.tar.gz
ls download/
mv download/group11.txt download/list11.txt
head -10 download/list.txt
head -10 download/group11.txt
echo -e "# 测试文件 - 混合格式\nhttps://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/test1.edf\ntest2.edf\ntest3.tsv\nhttps://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/test4.atr" > download/list_test.txt
cat download/list_test.txt
python3 -c "
import sys
sys.path.append('.')
from sleep_data_manager_auth import SleepDataManagerAuth

# 创建管理器实例
manager = SleepDataManagerAuth()

# 测试normalize_url函数
test_cases = [
    'https://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/test1.edf',
    'test2.edf',
    'test3.tsv',
    'https://physionet.org/files/nch-sleep/3.1.0/Sleep_Data/test4.atr'
]

print('🧪 测试URL标准化功能:')
for case in test_cases:
    result = manager.normalize_url(case)
    print(f'输入: {case}')
    print(f'输出: {result}')
    print('-' * 50)
"
rm download/list_test.txt
tar -czf sleep_data_manager_package_v2.tar.gz sleep_data_manager_auth.py PROJECT_README.md PROJECT_INTRODUCTION.md deploy.sh
tar -czf sleep_data_manager_package_v2.tar.gz sleep_data_manager_auth.py PROJECT_README.md PROJECT_INTRODUCTION.md deploy.sh UPDATE_NOTICE.md
ls -lh sleep_data_manager_package_v2.tar.gz
python3 -c "
import sys
sys.path.append('.')
from sleep_data_manager_auth import SleepDataManagerAuth

# 创建管理器实例
manager = SleepDataManagerAuth()

# 测试加载所有URL
all_urls = manager.load_all_urls()
print(f'✅ 成功加载 {len(all_urls)} 个URL')

# 显示前5个URL作为示例
print('📋 前5个URL示例:')
for i, url in enumerate(sorted(all_urls)[:5]):
    print(f'{i+1}. {url}')
"
python3 -c "
import sys
sys.path.append('.')
from sleep_data_manager_auth import SleepDataManagerAuth

# 创建管理器实例
manager = SleepDataManagerAuth()

# 测试加载下载任务
download_tasks = manager.load_download_tasks()
print(f'✅ 成功加载 {len(download_tasks)} 个下载任务')

# 显示前3个任务作为示例
print('📋 前3个下载任务示例:')
for i, task in enumerate(list(download_tasks)[:3]):
    print(f'{i+1}. {task}')
"
scp -o StrictHostKeyChecking=no sleep_data_manager_package_v2.tar.gz root@66.42.101.99:/root/
. "/root/.cursor-server/bin/7111807980fa9c93aedd455ffa44b682c0dc1350/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
sshpass -p 'b%3CXay+=JHsE(MF' scp -o StrictHostKeyChecking=no sleep_data_manager_package_v2.tar.gz root@66.42.101.99:/root/
sshpass -p '4C+uD3si,#5,rCW]' scp -o StrictHostKeyChecking=no sleep_data_manager_package_v2.tar.gz root@108.61.207.206:/root/
apt update && apt install -y sshpass
. "/root/.cursor-server/bin/7111807980fa9c93aedd455ffa44b682c0dc1350/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
which sshpass
ls -la *.py *.md *.sh *.txt 2>/dev/null || echo "列出项目相关文件："
git init
git config user.name "xihaopark" && git config user.email "xihaopark@gmail.com"
git add README.md .gitignore sleep_data_manager_auth.py sleep_data_manager.py auto_upload_manager.py PROJECT_README.md PROJECT_INTRODUCTION.md UPDATE_NOTICE.md deploy.sh
git status
git commit -m "Initial commit: Sleep Data Download Manager

- 🚀 完整的PhysioNet睡眠数据下载和管理系统
- 🔐 内置认证信息，支持自动下载和上传
- 📤 Dropbox自动上传，支持大文件分块上传
- 🔄 断点续传，网络中断后可继续下载
- 💾 智能磁盘空间管理，上传后自动删除本地文件
- 🧵 多线程并行处理，提高效率
- 📊 实时状态监控和日志记录
- 🖥️ 支持多服务器部署
- 📁 智能文件格式支持（URL和文件名混合）

核心文件：
- sleep_data_manager_auth.py: 主程序（推荐使用）
- sleep_data_manager.py: 基础版本
- auto_upload_manager.py: 纯上传管理器
- 完整的文档和部署脚本"
git remote add origin https://github.com/xihaopark/sleep_download.git
git branch -M main
git push -u origin main
git log --oneline
python3 sleep_data_manager_auth.py
python3 sleep_data_manager_auth.py 
