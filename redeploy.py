#!/usr/bin/env python3
"""
重新部署修复后的代码
"""

import paramiko
from pathlib import Path

SERVER_IP = "45.76.156.147"
SERVER_USER = "root"
SERVER_PASS = "2T=t9ZQqP5F%Nvau"
REMOTE_DIR = "/var/www/pricepulse"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

print("=== 重新部署修复后的代码 ===\n")

# 1. 停止服务
print("[1/4] 停止API服务...")
stdin, stdout, stderr = client.exec_command("systemctl stop pricepulse")
print(stdout.read().decode('utf-8'))

# 2. 上传修复后的文件
print("\n[2/4] 上传修复后的文件...")
code_dir = Path("/Users/gold/clawd/million-dollar-plan/code")

client.upload_file(str(code_dir / "crypto_collector.py"), f"{REMOTE_DIR}/code/crypto_collector.py")
client.upload_file(str(code_dir / "api_server.py"), f"{REMOTE_DIR}/code/api_server.py")

# 3. 创建数据目录
print("\n[3/4] 创建数据目录...")
stdin, stdout, stderr = client.exec_command(f"mkdir -p {REMOTE_DIR}/data")
print(stdout.read().decode('utf-8'))

# 4. 重启服务
print("\n[4/4] 重启服务...")
stdin, stdout, stderr = client.exec_command("systemctl start pricepulse")
print(stdout.read().decode('utf-8'))

# 等待几秒让服务启动
import time
time.sleep(3)

# 检查状态
print("\n检查服务状态...")
stdin, stdout, stderr = client.exec_command("systemctl status pricepulse --no-pager")
status = stdout.read().decode('utf-8')
print(status[:800])

# 测试API
print("\n测试API...")
stdin, stdout, stderr = client.exec_command("curl -s http://127.0.0.1:8000/api/prices | head -c 1000")
api_response = stdout.read().decode('utf-8')
print(api_response)

client.close()
print("\n重新部署完成！")
