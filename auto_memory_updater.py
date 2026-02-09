#!/usr/bin/env python3
"""
记忆更新守护进程
定期检查并更新项目状态快照
"""

import subprocess
import os
import time
from datetime import datetime
from pathlib import Path
import json

# 配置
PROJECT_DIR = Path("/Users/gold/clawd/million-dollar-plan")
SNAPSHOT_FILE = PROJECT_DIR / "SNAPSHOTS" / "latest.md"
API_URL = "https://pricepulse.top/api/prices"
STATUS_FILE = PROJECT_DIR / "AUTO_STATUS.json"
LOG_FILE = PROJECT_DIR / "auto-memory.log"

# 检查间隔（小时）
CHECK_INTERVAL = 2  # 每2小时检查一次

# 最大日志条数
MAX_LOG_LINES = 100

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    
    # 清理旧日志
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    
    if len(lines) > MAX_LOG_LINES:
        with open(LOG_FILE, "w") as f:
            f.writelines(lines[-MAX_LOG_LINES:])

def check_api_status():
    """检查API状态"""
    try:
        result = subprocess.run(
            ["curl", "-s", API_URL, "-o", "/dev/null", "-w", "%{http_code}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def get_current_status():
    """获取当前状态"""
    try:
        result = subprocess.run(
            ["curl", "-s", f"{API_URL}/health"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data
    except:
        pass
    
    # 如果API失败，从状态文件读取
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    
    return {}

def update_snapshot():
    """更新项目快照"""
    try:
        # 读取状态文件
        status = get_current_status()
        
        # 读取项目进度
        project_status = ""
        if SNAPSHOT_FILE.exists():
            with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
                project_status = f.read()
        
        # 创建新快照
        now = datetime.now().isoformat()
        
        snapshot_content = f"""# 价格脉动 - 自动快照

## 时间：{now}

## 当前状态

### 服务器状态
```
API状态: {'正常' if check_api_status() else '异常'}
数据采集: {'运行中' if status.get('collector_running') else '已停止'}
数据量: {status.get('data_count', '未知')}
最后更新: {status.get('last_update', '未知')}
```

### 项目进度
{project_status}

## 自动化记忆

### 说明
此文件由自动记忆更新守护进程定期更新。
如果你是新的会话，读取此文件即可了解完整的项目状态。

### 如何恢复
在新会话中告诉我：
```
读取项目状态：价格脉动
```
我会立即读取此文件并恢复所有进度。

---

最后更新：{now}
Token使用警告：如果token > 80%，停止主动开发，只保持服务运行

---
"""
        
        # 写入快照文件
        SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
            f.write(snapshot_content)
        
        # 更新状态文件
        with open(STATUS_FILE, 'w') as f:
            json.dump({
                'last_update': now,
                'api_status': check_api_status(),
                'project_status': 'loaded',
                'token_usage': 'unknown'
            }, f, indent=2)
        
        log("✅ 快照已更新")
        return True
        
    except Exception as e:
        log(f"❌ 更新快照失败: {e}")
        return False

def main():
    """主函数"""
    log("=== 记忆更新守护进程启动 ===")
    log(f"检查间隔: {CHECK_INTERVAL}小时")
    log(f"快照文件: {SNAPSHOT_FILE}")
    log(f"状态文件: {STATUS_FILE}")
    
    # 首次更新
    update_snapshot()
    
    # 定期检查和更新
    while True:
        try:
            log("等待下一次检查...")
            time.sleep(CHECK_INTERVAL * 3600)  # 转换为秒
            
            log("开始定期检查...")
            if update_snapshot():
                log("✅ 定期更新成功")
            else:
                log("⚠️  定期更新失败，但会继续尝试")
                
        except KeyboardInterrupt:
            log("\n👋 收到中断信号，守护进程退出")
            break
        except Exception as e:
            log(f"❌ 意外错误: {e}")
            time.sleep(60)  # 出错后等待1分钟再试

if __name__ == "__main__":
    main()
