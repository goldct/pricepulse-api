#!/usr/bin/env python3
"""
正确修复Nginx配置，指向/var/www/pricepulse/
"""

import paramiko

# 服务器配置
SERVER_IP = "45.76.156.147"
SERVER_USER = "root"
SERVER_PASS = "2T=t9ZQqP5F%Nvau"

print(f"=== 修复Nginx配置 ===")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
    print("✅ SSH连接成功\n")

    # 创建正确的Nginx配置
    print("[1/3] 创建Nginx配置...")
    nginx_config = '''
server {
    listen 80;
    listen [::]:80;
    server_name pricepulse.top _;

    # 重定向HTTP到HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name pricepulse.top _;

    # SSL证书
    ssl_certificate /etc/letsencrypt/live/pricepulse.top/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pricepulse.top/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 根目录
    root /var/www/pricepulse;
    index index_cn.html index.html;

    # 主页
    location = / {
        try_files $uri $uri/ /index_cn.html =404;
    }

    # 注册页面
    location = /register.html {
        try_files $uri $uri/ /register.html =404;
    }

    # 登录页面
    location = /login.html {
        try_files $uri $uri/ /login.html =404;
    }

    # 用户面板
    location = /dashboard.html {
        try_files $uri $uri/ /dashboard.html =404;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件缓存
    location ~* \\.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 启用gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;
    gzip_comp_level 6;
}
'''

    # 写入配置文件
    print("[2/3] 写入Nginx配置...")
    stdin, stdout, stderr = client.exec_command(
        'cat > /etc/nginx/sites-available/pricepulse << "ENDCONF"\n' +
        nginx_config +
        'ENDCONF'
    )

    if stderr.read():
        print(f"⚠️ 写入警告: {stderr.read().decode('utf-8')}")
    else:
        print("✅ 配置写入成功")

    # 创建符号链接
    print("\n[3/3] 启用配置...")
    stdin, stdout, stderr = client.exec_command("ln -sf /etc/nginx/sites-available/pricepulse /etc/nginx/sites-enabled/")
    print(stdout.read().decode('utf-8'))

    # 删除默认配置
    print("\n删除默认配置...")
    stdin, stdout, stderr = client.exec_command("rm -f /etc/nginx/sites-enabled/default")
    print("默认配置已删除")

    # 测试Nginx配置
    print("\n测试Nginx配置...")
    stdin, stdout, stderr = client.exec_command("nginx -t")
    test_result = stderr.read().decode('utf-8')

    if "syntax is ok" in test_result:
        print("✅ Nginx配置测试通过")
    else:
        print(f"❌ Nginx配置错误: {test_result}")
        print("不重启Nginx")
        client.close()
        exit(1)

    # 重启Nginx
    print("\n重启Nginx...")
    stdin, stdout, stderr = client.exec_command("systemctl restart nginx")
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        print("✅ Nginx重启成功")
    else:
        print(f"⚠️ Nginx重启警告: {stderr.read().decode('utf-8')}")

    # 验证配置
    print("\n验证配置...")
    stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/pricepulse | head -20")
    print(stdout.read().decode('utf-8'))

    client.close()

    print("\n" + "="*60)
    print("✅ 修复完成！")
    print("="*60)
    print("\n请清除浏览器缓存后测试：")
    print("https://pricepulse.top/register.html")
    print("https://pricepulse.top/login.html")
    print("https://pricepulse.top/dashboard.html")

except Exception as e:
    print(f"❌ 错误: {e}")
    client.close()
