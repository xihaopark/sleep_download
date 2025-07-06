# 敏感信息配置模板
# 请将此文件保存为 dropbox_config.py 并放在项目根目录

# Dropbox配置
DROPBOX_CONFIG = {
    'access_token': 'sl.u.AF34PeTlpglqeAYwABIYfeD3-SyW3tTUqkcjG_o5ffO0YJ9nT_G2pd1wHYFRqqv7z0-LFZ6jg6soFpe3KCUNDqulVlMPIWG-Mf80Jvbw72x6S9NJV-5-0IbRlbmGGF8c0B3qXaU',
    'app_key': 'bl4dllhus4upqu9',
    'app_secret': '54ppgfj4c2hagos',
    'refresh_token': 'your_refresh_token_here',  # 如果有的话
    'upload_folder': '/sleep_data'  # Dropbox上传目录
}

# PhysioNet登录信息（如果需要认证下载）
PHYSIONET_CONFIG = {
    'username': 'chenzcha',
    'password': '97HU15lWcE'
}

# 下载配置
DOWNLOAD_CONFIG = {
    'max_concurrent_downloads': 3,  # 最大并发下载数
    'retry_attempts': 3,           # 重试次数
    'download_timeout': 300,       # 下载超时时间（秒）
    'check_interval': 30,          # 检查间隔（秒）
    'min_free_space_gb': 5,        # 最小剩余空间（GB）
    'max_file_size_gb': 10         # 单文件最大大小（GB）
}

# 上传配置
UPLOAD_CONFIG = {
    'upload_after_download': True,  # 下载后立即上传
    'delete_after_upload': True,    # 上传后删除本地文件
    'upload_chunk_size': 8 * 1024 * 1024,  # 8MB chunks
    'max_upload_retries': 3,        # 上传重试次数
    'verify_upload': True           # 验证上传完整性
}

# 日志配置
LOG_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'sleep_data_manager.log',
    'max_log_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# 通知配置（可选）
NOTIFICATION_CONFIG = {
    'enable_notifications': False,
    'webhook_url': '',  # 如果需要通知的话
    'notify_on_error': True,
    'notify_on_completion': True
} 