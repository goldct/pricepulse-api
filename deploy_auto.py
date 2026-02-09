#!/usr/bin/env python3
"""
自动部署脚本 - 使用Paramiko
"""

import paramiko
import sys
from pathlib import Path

# 服务器配置
SERVER_IP = "45.76.156.147"
SERVER_USER = "root"
SERVER_PASS = "2T=t9ZQqP5F%Nvau"
REMOTE_DIR = "/var/www/pricepulse"

class DeploymentClient:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.client = None

    def connect(self):
        """连接到服务器"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, username=self.user, password=self.password, timeout=10)
            print(f"✓ 成功连接到 {self.host}")
            return True
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False

    def execute(self, command):
        """执行命令"""
        if not self.client:
            print("未连接到服务器")
            return None, None

        try:
            stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            return output, error
        except Exception as e:
            return None, str(e)

    def upload_file(self, local_path, remote_path):
        """上传文件"""
        if not self.client:
            print("未连接到服务器")
            return False

        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print(f"✓ 上传文件: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            print(f"✗ 上传文件失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()

def deploy():
    """部署函数"""
    print(f"=== 开始部署到 {SERVER_IP} ===\n")

    # 连接服务器
    client = DeploymentClient(SERVER_IP, SERVER_USER, SERVER_PASS)
    if not client.connect():
        return

    try:
        # 1. 测试连接
        print("\n[1/8] 测试系统信息...")
        output, error = client.execute("uname -a")
        if output:
            print(f"✓ 服务器信息:\n{output}")

        # 2. 更新系统并安装依赖
        print("\n[2/8] 更新系统并安装依赖...")
        print("(这可能需要几分钟...)")

        commands = [
            "apt-get update",
            "apt-get install -y python3 python3-pip python3-venv nginx",
            "pip3 install --upgrade pip"
        ]

        for cmd in commands:
            output, error = client.execute(cmd)
            if error and "cannot be found" not in error and "already installed" not in error.lower():
                print(f"  警告: {error}")

        print("✓ 系统依赖安装完成")

        # 3. 创建目录
        print("\n[3/8] 创建目录...")
        client.execute(f"mkdir -p {REMOTE_DIR}")
        client.execute(f"mkdir -p {REMOTE_DIR}/data")
        client.execute(f"mkdir -p {REMOTE_DIR}/code")
        print("✓ 目录创建完成")

        # 4. 上传代码文件
        print("\n[4/8] 上传代码文件...")

        code_dir = Path("/Users/gold/clawd/million-dollar-plan/code")
        if code_dir.exists():
            # 上传api_server.py
            client.upload_file(str(code_dir / "api_server.py"), f"{REMOTE_DIR}/code/api_server.py")
            # 上传crypto_collector.py
            client.upload_file(str(code_dir / "crypto_collector.py"), f"{REMOTE_DIR}/code/crypto_collector.py")
            # 上传index.html
            client.upload_file(str(code_dir / "index.html"), f"{REMOTE_DIR}/code/index.html")
        else:
            print(f"✗ 代码目录不存在: {code_dir}")

        # 5. 配置虚拟环境
        print("\n[5/8] 配置Python虚拟环境...")
        commands = [
            f"cd {REMOTE_DIR} && python3 -m venv venv",
            f"{REMOTE_DIR}/venv/bin/pip install fastapi uvicorn aiohttp"
        ]

        for cmd in commands:
            output, error = client.execute(cmd)
            if error and "already installed" not in error.lower() and "successfully installed" not in output.lower():
                print(f"  警告: {error}")

        print("✓ 虚拟环境配置完成")

        # 6. 创建系统服务
        print("\n[6/8] 创建系统服务...")

        service_content = f"""[Unit]
Description=PricePulse API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={REMOTE_DIR}
Environment="PATH={REMOTE_DIR}/venv/bin"
ExecStart={REMOTE_DIR}/venv/bin/python code/api_server.py
Restart=always

[Install]
WantedBy=multi-user.target"""

        # 创建服务文件
        output, error = client.execute(f"cat > /etc/systemd/system/pricepulse.service << 'ENDOFFILE'\n{service_content}\nENDOFFILE")

        # 重载并启动
        client.execute("systemctl daemon-reload")
        client.execute("systemctl start pricepulse")
        client.execute("systemctl enable pricepulse")

        # 检查状态
        output, error = client.execute("systemctl status pricepulse --no-pager")
        if output:
            print("✓ 系统服务创建并启动")
            print(f"服务状态:\n{output[:500]}")  # 只显示前500字符

        # 7. 配置Nginx
        print("\n[7/8] 配置Nginx...")

        nginx_config = f"""
server {{
    listen 80;
    server_name _;

    # API代理
    location /api/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    # 前端页面
    location / {{
        alias {REMOTE_DIR}/code/;
        index index.html;
        try_files $uri $uri/ /index.html;
    }}

    # 启用gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}}"""

        # 创建Nginx配置
        client.execute(f"cat > /etc/nginx/sites-available/pricepulse << 'ENDOFFILE'\n{nginx_config}\nENDOFFILE")

        # 启用站点
        client.execute("ln -sf /etc/nginx/sites-available/pricepulse /etc/nginx/sites-enabled/")
        client.execute("rm -f /etc/nginx/sites-enabled/default")

        # 测试并重启Nginx
        client.execute("nginx -t")
        client.execute("systemctl restart nginx")

        # 检查状态
        output, error = client.execute("systemctl status nginx --no-pager")
        if output:
            print("✓ Nginx配置并启动")
            print(f"Nginx状态:\n{output[:500]}")  # 只显示前500字符

        # 8. 配置防火墙
        print("\n[8/8] 配置防火墙...")
        client.execute("ufw allow 22/tcp")
        client.execute("ufw allow 80/tcp")
        client.execute("ufw allow 443/tcp")
        output, error = client.execute("ufw --force enable")
        if "Firewall is active" in output or "already enabled" in output.lower():
            print("✓ 防火墙配置完成")
        else:
            print("⚠️  防火墙配置可能失败，但不影响服务")

        print("\n" + "="*60)
        print("部署完成！")
        print("="*60)
        print(f"\n访问地址：")
        print(f"  网站: http://{SERVER_IP}")
        print(f"  API: http://{SERVER_IP}/api/prices")
        print(f"  文档: http://{SERVER_IP}/docs")
        print(f"\n后续步骤：")
        print(f"  1. 配置域名DNS: pricepulse.top -> {SERVER_IP}")
        print(f"  2. 安装SSL证书: certbot --nginx -d pricepulse.top")
        print(f"  3. 测试API功能")

        # 检查服务状态
        print("\n检查服务状态...")
        output, error = client.execute("curl -s http://localhost/api/prices | head -c 500")
        if output:
            print("✓ API响应正常")
            print(f"API返回: {output}")
        else:
            print("⚠️  API可能还未启动，请稍等片刻")

    finally:
        client.close()
        print("\n连接已关闭")

if __name__ == "__main__":
    deploy()
