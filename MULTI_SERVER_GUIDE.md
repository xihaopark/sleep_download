# 多服务器Dropbox Token管理指南

## 🎯 问题场景
在多个服务器上运行睡眠数据下载上传系统时，需要共享和同步Dropbox访问令牌。

## 🔧 解决方案

### 方案1: GitHub同步（推荐）

#### 步骤1: 主服务器获取新token
```bash
# 在主服务器上
python3 token_manager.py auth
# 复制URL到浏览器授权，获取authorization code

# 使用code获取token并推送到GitHub
python3 sync_token_across_servers.py push <authorization_code>
```

#### 步骤2: 其他服务器同步token
```bash
# 在其他服务器上
python3 sync_token_across_servers.py github
```

#### 步骤3: 设置自动同步
```bash
# 创建自动同步脚本
python3 sync_token_across_servers.py create-script

# 后台运行自动同步
nohup ./auto_sync_token.sh > logs/token_sync.log 2>&1 &
```

### 方案2: 共享文件系统同步

如果服务器之间有共享存储（如NFS、CIFS等）：

```bash
# 设置共享目录
SHARED_PATH="/shared/tokens"

# 主服务器更新token后
python3 token_manager.py update <auth_code>
cp shared_token.json $SHARED_PATH/

# 其他服务器同步
python3 sync_token_across_servers.py shared $SHARED_PATH
```

### 方案3: 手动同步

```bash
# 主服务器获取token
python3 token_manager.py auth
python3 token_manager.py update <auth_code>

# 复制shared_token.json到其他服务器
scp shared_token.json user@server2:/path/to/project/
scp shared_token.json user@server3:/path/to/project/

# 其他服务器应用token
python3 token_manager.py validate
```

## 🔄 工作流程

### 正常运行流程
1. **启动时检查**: 每个服务器启动时自动检查token有效性
2. **定时同步**: 每5分钟从GitHub或共享存储同步token
3. **失败处理**: 如果token无效，暂停上传并记录错误
4. **自动恢复**: 一旦检测到新的有效token，自动恢复上传

### Token过期处理
1. **检测过期**: 系统自动检测401错误
2. **通知管理员**: 记录到日志并显示错误信息
3. **暂停上传**: 停止上传，继续下载
4. **等待更新**: 等待新token同步后自动恢复

## 📋 使用命令

### Token管理器命令
```bash
# 查看token状态
python3 token_manager.py status

# 获取授权URL
python3 token_manager.py auth

# 更新token
python3 token_manager.py update <auth_code>

# 验证token
python3 token_manager.py validate
```

### 同步管理命令
```bash
# 从GitHub同步
python3 sync_token_across_servers.py github

# 推送到GitHub
python3 sync_token_across_servers.py push <auth_code>

# 从共享文件夹同步
python3 sync_token_across_servers.py shared /path/to/shared

# 创建自动同步脚本
python3 sync_token_across_servers.py create-script
```

## 🛠️ 部署示例

### 三服务器部署示例

#### 服务器1 (主服务器)
```bash
# 初始化并获取token
git clone https://github.com/xihaopark/sleep_download.git
cd sleep_download
python3 setup_config.py

# 获取新token并推送
python3 token_manager.py auth
# 在浏览器中授权后获取code
python3 sync_token_across_servers.py push <auth_code>

# 启动下载上传
./quick_start.sh
```

#### 服务器2 & 3 (从服务器)
```bash
# 克隆项目
git clone https://github.com/xihaopark/sleep_download.git
cd sleep_download

# 配置基本信息（除了token）
python3 setup_config.py

# 从GitHub同步token
python3 sync_token_across_servers.py github

# 设置自动同步
python3 sync_token_across_servers.py create-script
nohup ./auto_sync_token.sh > logs/token_sync.log 2>&1 &

# 启动下载上传
./quick_start.sh
```

## 🔐 安全考虑

### GitHub方式
- ✅ 优点: 自动化程度高，易于管理
- ⚠️ 注意: token会存储在GitHub仓库中
- 🔒 建议: 使用私有仓库

### 共享文件系统方式
- ✅ 优点: 完全内网，安全性高
- ⚠️ 注意: 需要配置共享存储
- 🔒 建议: 设置适当的文件权限

### 手动同步方式
- ✅ 优点: 完全可控，最安全
- ⚠️ 注意: 需要手动操作
- 🔒 建议: 定期更新token

## 📊 监控和维护

### 日志监控
```bash
# 查看token同步日志
tail -f logs/token_sync.log

# 查看主程序日志
tail -f logs/wget_manager.log

# 检查token状态
python3 token_manager.py status
```

### 定期维护
```bash
# 每月检查一次token状态
python3 token_manager.py validate

# 清理旧的token备份
find . -name "token_backup_*.json" -mtime +30 -delete

# 更新系统
git pull origin main
```

## 🆘 故障排除

### 常见问题

1. **Token同步失败**
   ```bash
   # 检查网络连接
   ping github.com
   
   # 检查Git配置
   git status
   git remote -v
   
   # 手动同步
   git pull origin main
   ```

2. **Token验证失败**
   ```bash
   # 检查token格式
   python3 token_manager.py validate
   
   # 重新获取token
   python3 token_manager.py auth
   ```

3. **上传401错误**
   ```bash
   # 立即同步新token
   python3 sync_token_across_servers.py github
   
   # 重启上传程序
   ./manage.sh restart
   ```

### 紧急恢复
```bash
# 如果所有服务器token都失效
# 1. 在任一服务器获取新token
python3 token_manager.py auth
python3 token_manager.py update <new_auth_code>

# 2. 推送到GitHub
python3 sync_token_across_servers.py push <new_auth_code>

# 3. 其他服务器同步
python3 sync_token_across_servers.py github

# 4. 重启所有服务器的程序
./manage.sh restart
```

## 🎯 最佳实践

1. **使用主从架构**: 指定一个主服务器负责token更新
2. **定时检查**: 每天检查一次token状态
3. **备份策略**: 保留token备份文件
4. **监控告警**: 设置token过期告警
5. **文档更新**: 记录每次token更新的时间和原因 