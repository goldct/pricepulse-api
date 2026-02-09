#!/usr/bin/env python3
"""
启动脚本 - 启动API服务器
"""

import subprocess
import sys
import os

# 确保在正确的目录
os.chdir("/Users/gold/clawd/million-dollar-plan/code")

# 激活虚拟环境并运行
venv_python = "/Users/gold/clawd/million-dollar-plan/venv/bin/python"

# 启动API服务器
cmd = [venv_python, "api_server.py"]

print("启动API服务器...")
print(f"命令: {' '.join(cmd)}")
print("API地址: http://localhost:8000")
print("API文档: http://localhost:8000/docs")
print("\n按 Ctrl+C 停止\n")

subprocess.run(cmd)
