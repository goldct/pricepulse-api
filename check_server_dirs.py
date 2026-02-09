#!/usr/bin/env python3
"""
检查服务器上的文件并访问测试
"""

import paramiko

# 服务器配置
SERVER_IP = "45.76.156.147"
SERVER_USER = "root"
SERVER_PASS = "2T=t9ZQqP5F%Nvau"

print(f"=== 检查服务器文件 ===")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
    print("✅ SSH连接成功\n")

    # 检查/var/www/pricepulse/和/var/www/html/
    print("[1/3] 检查两个目录...")
    stdin, stdout, stderr = client.exec_command("ls -lh /var/www/ 2>&1")
    print(stdout.read().decode('utf-8'))
    
    print("\n/var/www/pricepulse/内容:")
    stdin, stdout, stderr = client.exec_command("ls -lh /var/www/pricepulse/ 2>&1")
    print(stdout.read().decode('utf-8'))

    # 检查Nginx根目录配置
    print("\n[2/3] 检查Nginx根目录配置...")
    stdin, stdout, stderr = client.exec_command("cat /etc/nginx/nginx.conf | grep -A5 'root' 2>&1")
    print(stdout.read().decode('utf-8'))

    # 检查是否安装了pricepulse的配置文件
    print("\n[3/3] 检查pricepulse Nginx配置...")
    stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/pricepulse 2>&1 || echo '配置不存在'")
    print(stdout.read().decode('utf-8'))

    client.close()

    print("\n" + "="*60)
    print("检查完成")
    print("="*60)

except Exception as e:
    print(f"❌ 错误: {e}")
    client.close()
