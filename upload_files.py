#!/usr/bin/env python3
"""
上传前端文件到服务器
"""

import paramiko
import os

# 服务器配置
SERVER_IP = "45.76.156.147"
SERVER_USER = "root"
SERVER_PASS = "2T=t9ZQpP5F%Nvau"
REMOTE_DIR = "/var/www/pricepulse"

# 要上传的文件
FILES_TO_UPLOAD = [
    "/Users/gold/clawd/million-dollar-plan/code/register.html",
    "/Users/gold/clawd/million-dollar-plan/code/login.html",
    "/Users/gold/clawd/million-dollar-plan/code/dashboard.html"
]

print("=== 开始上传前端文件 ===\n")

# 连接SSH
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"[1/3] 连接到服务器 {SERVER_IP}...")
    client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
    print("✅ 连接成功\n")

    # 创建SFTP客户端
    sftp = client.open_sftp()

    # 上传每个文件
    print("[2/3] 上传文件...")
    for i, file_path in enumerate(FILES_TO_UPLOAD, 1):
        filename = os.path.basename(file_path)
        remote_path = f"{REMOTE_DIR}/{filename}"

        print(f"  [{i}/{len(FILES_TO_UPLOAD)}] 上传 {filename}...")
        sftp.put(file_path, remote_path)
        print(f"  ✅ {filename} 上传成功")

    sftp.close()
    print("\n✅ 所有文件上传完成\n")

    # 重启Nginx
    print("[3/3] 重启Nginx...")
    stdin, stdout, stderr = client.exec_command("systemctl restart nginx")
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        print("✅ Nginx重启成功\n")
    else:
        print(f"⚠️ Nginx重启失败: {stderr.read().decode('utf-8')}\n")

    # 验证文件
    print("=== 验证上传的文件 ===")
    stdin, stdout, stderr = client.exec_command(f"ls -lh {REMOTE_DIR}/*.html")
    print(stdout.read().decode('utf-8'))

    print("\n=== 上传完成 ===")
    print(f"访问以下链接验证:")
    print(f"  • 注册页面: https://pricepulse.top/register.html")
    print(f"  • 登录页面: https://pricepulse.top/login.html")
    print(f"  • 用户面板: https://pricepulse.top/dashboard.html")

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    client.close()
