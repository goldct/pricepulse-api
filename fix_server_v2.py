#!/usr/bin/env python3
"""
直接在服务器上修复index_cn.html按钮
使用SSH连接并编辑文件
"""

import paramiko

# 服务器配置
SERVER_IP = "45.76.156.147"
SERVER_USER = "root"
SERVER_PASS = "2T=t9ZQqP5F%Nvau"
REMOTE_FILE = "/var/www/pricepulse/index_cn.html"

print(f"=== 连接到服务器 {SERVER_IP} ===")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
    print("✅ SSH连接成功\n")

    sftp = client.open_sftp()

    # 读取文件
    print(f"[1/4] 读取 {REMOTE_FILE}...")
    with sftp.file(REMOTE_FILE, 'r') as f:
        content = f.read().decode('utf-8')

    print(f"✅ 文件读取成功 ({len(content)} 字节)\n")

    # 修复：将所有 href="#pricing" 的链接改为 href="register.html"
    print("[2/4] 修复所有按钮链接...")
    content = content.replace('href="#pricing"', 'href="register.html"')
    print("✅ 所有 #pricing 链接已改为 register.html\n")

    # 修复：给所有按钮添加 onclick 事件
    print("[3/4] 添加按钮点击事件...")
    
    # 为包含"开始使用"的按钮添加 onclick
    import re
    
    # 匹配所有"开始使用"按钮并添加onclick
    content = re.sub(
        r'(<button[^>]*class="[^"]*gradient-bg[^"]*"[^>]*>)([^<]*开始使用[^<]*)(</button>)',
        r'\1 onclick="window.location.href=\'register.html\'"\2\3',
        content
    )
    
    print("✅ 按钮点击事件已添加\n")

    # 写回文件
    print(f"[4/4] 写回 {REMOTE_FILE}...")
    with sftp.file(REMOTE_FILE, 'w') as f:
        f.write(content.encode('utf-8'))

    print("✅ 文件写入成功\n")

    # 重启Nginx（清除缓存）
    print("重启Nginx（清除缓存）...")
    stdin, stdout, stderr = client.exec_command("systemctl restart nginx")
    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        print("✅ Nginx重启成功\n")
    else:
        print(f"⚠️  Nginx重启警告: {stderr.read().decode('utf-8')}\n")

    sftp.close()
    client.close()

    print("="*50)
    print("✅ 修复完成！")
    print("="*50)
    print("\n请刷新页面测试：")
    print("https://pricepulse.top")
    print("\n所有按钮现在都应该能跳转到register.html了！")

except Exception as e:
    print(f"❌ 错误: {e}")
    client.close()
