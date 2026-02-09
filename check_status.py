#!/usr/bin/env python3
"""
检查服务器状态
"""

import paramiko

# 服务器配置
SERVER_IP = "45.76.156.147"
SERVER_USER = "root"
SERVER_PASS = "2T=t9ZQqP5F%Nvau"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

print("=== 检查服务状态 ===\n")

# 检查API服务状态
print("[1] API服务状态:")
stdin, stdout, stderr = client.exec_command("systemctl status pricepulse --no-pager")
print(stdout.read().decode('utf-8')[:500])

# 检查API服务日志
print("\n[2] API服务日志:")
stdin, stdout, stderr = client.exec_command("journalctl -u pricepulse -n 30 --no-pager")
print(stdout.read().decode('utf-8'))

# 检查8000端口
print("\n[3] 检查8000端口:")
stdin, stdout, stderr = client.exec_command("netstat -tlnp | grep 8000")
print(stdout.read().decode('utf-8'))

# 测试本地API
print("\n[4] 测试本地API:")
stdin, stdout, stderr = client.exec_command("curl -s http://127.0.0.1:8000/api/prices | head -c 500")
print(stdout.read().decode('utf-8'))

client.close()
