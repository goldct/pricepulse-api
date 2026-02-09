#!/bin/bash
# 服务器部署脚本
# 使用方法：./deploy.sh <服务器IP> <用户名>

SERVER_IP=$1
SERVER_USER=${2:-root}
REMOTE_DIR="/var/www/crypto-pulse"
API_PORT=8000

echo "=== Crypto Pulse 部署脚本 ==="
echo "服务器: $SERVER_USER@$SERVER_IP"
echo "远程目录: $REMOTE_DIR"
echo ""

# 1. 复制文件到服务器
echo "[1/5] 复制文件到服务器..."
scp -r \
  code/ \
  venv/ \
  data/ \
  $SERVER_USER@$SERVER_IP:$REMOTE_DIR/

# 2. 在服务器上安装依赖
echo "[2/5] 安装系统依赖..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
    # 更新系统
    sudo apt-get update

    # 安装Python和必要工具
    sudo apt-get install -y python3 python3-pip python3-venv nginx

    # 安装防火墙
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw allow 8000
    sudo ufw --force enable

    echo "系统依赖安装完成"
ENDSSH

# 3. 配置虚拟环境
echo "[3/5] 配置虚拟环境..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
    cd /var/www/crypto-pulse

    # 激活虚拟环境
    source venv/bin/activate

    # 确保安装了所有依赖
    pip install --upgrade pip
    pip install fastapi uvicorn aiohttp

    echo "虚拟环境配置完成"
ENDSSH

# 4. 创建系统服务
echo "[4/5] 创建系统服务..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
    # 创建服务文件
    sudo tee /etc/systemd/system/crypto-pulse.service > /dev/null <<EOT
[Unit]
Description=Crypto Pulse API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/crypto-pulse
Environment="PATH=/var/www/crypto-pulse/venv/bin"
ExecStart=/var/www/crypto-pulse/venv/bin/python code/api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOT

    # 重载systemd
    sudo systemctl daemon-reload

    # 启动服务
    sudo systemctl start crypto-pulse

    # 设置开机自启
    sudo systemctl enable crypto-pulse

    echo "服务创建完成"
ENDSSH

# 5. 配置Nginx
echo "[5/5] 配置Nginx..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
    # 创建Nginx配置
    sudo tee /etc/nginx/sites-available/crypto-pulse > /dev/null <<EOT
server {
    listen 80;
    server_name _;

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 前端页面
    location / {
        alias /var/www/crypto-pulse/code/;
        index index.html;
    }

    # 启用gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
EOT

    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/crypto-pulse /etc/nginx/sites-enabled/

    # 测试配置
    sudo nginx -t

    # 重启Nginx
    sudo systemctl restart nginx

    echo "Nginx配置完成"
ENDSSH

echo ""
echo "=== 部署完成 ==="
echo "API地址: http://$SERVER_IP/api/prices"
echo "前端页面: http://$SERVER_IP"
echo ""
echo "检查服务状态:"
echo "  ssh $SERVER_USER@$SERVER_IP 'sudo systemctl status crypto-pulse'"
echo "  ssh $SERVER_USER@$SERVER_IP 'sudo systemctl status nginx'"
echo ""
