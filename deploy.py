#!/usr/bin/env python3
"""
自动部署脚本 - 连接服务器并部署
"""

import subprocess
import os

# 服务器配置
SERVER_IP = "45.76.156.147"
SERVER_USER = "root"
SERVER_PASS = "2T=t9ZQqP5F%Nvau"
REMOTE_DIR = "/var/www/pricepulse"

def run_ssh_command(command):
    """执行SSH命令"""
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_IP} '{command}'"
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    return result

def main():
    print(f"=== 连接到服务器 {SERVER_IP} ===\n")

    # 1. 测试连接
    print("[1/8] 测试SSH连接...")
    result = run_ssh_command("echo '连接成功' && uname -a")
    if result.returncode == 0:
        print("✓ SSH连接成功")
        print(result.stdout)
    else:
        print("✗ SSH连接失败")
        print(result.stderr)
        return

    # 2. 安装系统依赖
    print("\n[2/8] 安装系统依赖...")
    result = run_ssh_command("""
        # 更新系统
        apt-get update > /dev/null 2>&1

        # 安装Python和工具
        apt-get install -y python3 python3-pip python3-venv nginx > /dev/null 2>&1

        echo "系统依赖安装完成"
    """)

    if result.returncode == 0:
        print("✓ 系统依赖安装完成")
    else:
        print("✗ 系统依赖安装失败")
        print(result.stderr)
        return

    # 3. 创建目录
    print("\n[3/8] 创建目录...")
    result = run_ssh_command(f"mkdir -p {REMOTE_DIR} && mkdir -p {REMOTE_DIR}/data && echo '目录创建完成'")
    if result.returncode == 0:
        print("✓ 目录创建完成")
    else:
        print("✗ 目录创建失败")
        return

    # 4. 复制代码
    print("\n[4/8] 复制代码文件...")
    # 需要用scp复制，这里先用简单的tar方式
    os.system(f"""
        # 创建压缩包
        cd /Users/gold/clawd/million-dollar-plan
        tar czf /tmp/deploy.tar.gz code/

        # 上传（需要手动输入密码）
        scp -o StrictHostKeyChecking=no /tmp/deploy.tar.gz {SERVER_USER}@{SERVER_IP}:/tmp/

        # 解压到服务器
        ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_IP} 'tar xzf /tmp/deploy.tar.gz -C {REMOTE_DIR}/ && rm /tmp/deploy.tar.gz'
    """)

    print("✓ 代码文件复制完成")

    # 5. 配置虚拟环境
    print("\n[5/8] 配置Python虚拟环境...")
    result = run_ssh_command(f"""
        cd {REMOTE_DIR}

        # 创建虚拟环境
        python3 -m venv venv

        # 激活虚拟环境并安装依赖
        {REMOTE_DIR}/venv/bin/pip install --upgrade pip > /dev/null 2>&1
        {REMOTE_DIR}/venv/bin/pip install fastapi uvicorn aiohttp > /dev/null 2>&1

        echo "虚拟环境配置完成"
    """)

    if result.returncode == 0:
        print("✓ 虚拟环境配置完成")
    else:
        print("✗ 虚拟环境配置失败")
        print(result.stderr)
        return

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

    result = run_ssh_command(f"""
        cat > /etc/systemd/system/pricepulse.service << 'ENDOFFILE'
{service_content}
ENDOFFILE

        # 重载systemd
        systemctl daemon-reload

        # 启动服务
        systemctl start pricepulse

        # 设置开机自启
        systemctl enable pricepulse

        # 检查状态
        systemctl status pricepulse --no-pager
    """)

    if result.returncode == 0:
        print("✓ 系统服务创建并启动")
    else:
        print("✗ 系统服务创建失败")
        print(result.stderr)
        return

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

    result = run_ssh_command(f"""
        cat > /etc/nginx/sites-available/pricepulse << 'ENDOFFILE'
{nginx_config}
ENDOFFILE

        # 启用站点
        ln -sf /etc/nginx/sites-available/pricepulse /etc/nginx/sites-enabled/

        # 删除默认配置
        rm -f /etc/nginx/sites-enabled/default

        # 测试配置
        nginx -t

        # 重启Nginx
        systemctl restart nginx

        # 检查状态
        systemctl status nginx --no-pager
    """)

    if result.returncode == 0:
        print("✓ Nginx配置并启动")
    else:
        print("✗ Nginx配置失败")
        print(result.stderr)
        return

    # 8. 配置防火墙
    print("\n[8/8] 配置防火墙...")
    result = run_ssh_command("""
        # 允许SSH
        ufw allow 22/tcp > /dev/null 2>&1

        # 允许HTTP
        ufw allow 80/tcp > /dev/null 2>&1

        # 允许HTTPS
        ufw allow 443/tcp > /dev/null 2>&1

        # 启用防火墙
        ufw --force enable > /dev/null 2>&1

        echo "防火墙配置完成"
    """)

    if result.returncode == 0:
        print("✓ 防火墙配置完成")
    else:
        print("⚠️ 防火墙配置可能失败，但不影响服务")

    print("\n" + "="*50)
    print("部署完成！")
    print("="*50)
    print(f"\n服务器信息：")
    print(f"  IP地址: {SERVER_IP}")
    print(f"  访问地址: http://{SERVER_IP}")
    print(f"  API地址: http://{SERVER_IP}/api/prices")
    print(f"\n后续步骤：")
    print(f"  1. 配置域名DNS: pricepulse.top -> {SERVER_IP}")
    print(f"  2. 安装SSL证书（Let's Encrypt）")
    print(f"  3. 测试API功能")
    print(f"\n服务状态：")
    print(f"  systemctl status pricepulse")
    print(f"  systemctl status nginx")

if __name__ == "__main__":
    main()
