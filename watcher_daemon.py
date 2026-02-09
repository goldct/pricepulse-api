#!/usr/bin/env python3
"""
守护唤醒器
监控指令接收，超时后自动发送唤醒指令
"""

import subprocess
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

# 配置
PROJECT_DIR = Path("/Users/gold/clawd/million-dollar-plan")
STATUS_FILE = PROJECT_DIR / "AUTO_STATUS.json"
WATCH_DIR = PROJECT_DIR
LOG_FILE = PROJECT_DIR / "watcher.log"

# 监控配置
CHECK_INTERVAL = 300  # 每分钟检查一次（300秒）
TIMEOUT_MINUTES = 60   # 超过60分钟没收到指令就唤醒
MAX_LOG_LINES = 50

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

def update_last_activity():
    """更新最后活动时间"""
    now = datetime.now().isoformat()
    
    try:
        status = {
            'last_activity': now,
            'last_wake': now,
            'watcher_running': True,
            'status': 'monitoring'
        }
        
        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f, indent=2)
        
        log("✅ 活动时间已更新")
        return True
    except Exception as e:
        log(f"❌ 更新活动时间失败: {e}")
        return False

def get_last_activity():
    """获取最后活动时间"""
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def send_wake_command():
    """发送唤醒指令"""
    now = datetime.now().isoformat()
    
    log(f"🔔 发送唤醒指令: {now}")
    
    # 更新最后唤醒时间
    try:
        status = get_last_activity()
        if status:
            status['last_wake'] = now
            status['wake_count'] = status.get('wake_count', 0) + 1
            
            with open(STATUS_FILE, 'w') as f:
                json.dump(status, f, indent=2)
    except Exception as e:
        log(f"❌ 更新唤醒记录失败: {e}")
    
    # 触发Moltbot通知
    try:
        # 使用echo命令写入一个触发文件
        trigger_file = PROJECT_DIR / "WAKE_TRIGGER.txt"
        trigger_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(trigger_file, 'w') as f:
            f.write(f"{now}\nWAKE_UP\n")
        
        log(f"✅ 唤醒触发文件已创建: {trigger_file}")
    except Exception as e:
        log(f"❌ 创建触发文件失败: {e}")
    
    return True

def check_need_wake():
    """检查是否需要唤醒"""
    status = get_last_activity()
    
    if not status:
        log("⚠️  未找到状态文件，记录当前活动")
        update_last_activity()
        return False
    
    last_activity = status.get('last_activity')
    if not last_activity:
        log("⚠️  未找到活动时间，记录当前活动")
        update_last_activity()
        return False
    
    # 计算时间差
    last_time = datetime.fromisoformat(last_activity)
    time_diff = datetime.now() - last_time
    
    # 检查文件修改时间
    status_file_age = datetime.now() - datetime.fromtimestamp(STATUS_FILE.stat().st_mtime)
    
    log(f"上次活动: {last_time}")
    log(f"已过去: {time_diff}")
    log(f"状态文件年龄: {status_file_age}")
    log(f"唤醒阈值: {timedelta(minutes=TIMEOUT_MINUTES)}")
    
    # 如果超过阈值，发送唤醒指令
    if time_diff > timedelta(minutes=TIMEOUT_MINUTES):
        log(f"⏰ 超时{TIMEOUT_MINUTES}分钟，准备唤醒")
        return send_wake_command()
    elif status_file_age > timedelta(minutes=TIMEOUT_MINUTES):
        log(f"⏰ 状态文件超过{TIMEOUT_MINUTES}分钟未更新，可能异常")
        return send_wake_command()
    else:
        log(f"✅ 正常监控中")
        return False

def watch_for_new_files():
    """监听新文件或文件修改"""
    current_files = set()
    
    try:
        for file in WATCH_DIR.glob('*'):
            if file.is_file():
                current_files.add(file.name)
        
        log(f"当前文件数: {len(current_files)}")
        update_last_activity()
        
    except Exception as e:
        log(f"❌ 监听文件失败: {e}")

def check_api_health():
    """检查API健康状态"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
             "https://pricepulse.top/api/health"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        api_healthy = result.returncode == 200
        log(f"API健康检查: {'✅ 正常' if api_healthy else '❌ 异常'}")
        
        if api_healthy:
            update_last_activity()
        
        return api_healthy
        
    except Exception as e:
        log(f"❌ API健康检查失败: {e}")
        return False

def main():
    """主函数"""
    log("=== 守护唤醒器启动 ===")
    log(f"检查间隔: {CHECK_INTERVAL}秒 ({CHECK_INTERVAL/60:.1f}分钟)")
    log(f"唤醒超时: {TIMEOUT_MINUTES}分钟")
    log(f"监控目录: {WATCH_DIR}")
    log(f"状态文件: {STATUS_FILE}")
    
    # 首次运行，记录状态
    if not STATUS_FILE.exists():
        log("首次运行，初始化状态文件")
        update_last_activity()
    
    # 初始文件扫描
    watch_for_new_files()
    
    # 主循环
    log("开始主监控循环...")
    
    while True:
        try:
            # 检查超时
            log("检查超时...")
            if check_need_wake():
                log("🔔 唤醒指令已发送")
            else:
                log("✅ 无需唤醒")
            
            # 检查API健康
            log("检查API健康...")
            if check_api_health():
                log("✅ API健康")
            else:
                log("⚠️  API异常")
            
            # 监听文件变化
            log("监听文件变化...")
            watch_for_new_files()
            
            # 等待下一次检查
            log(f"等待 {CHECK_INTERVAL} 秒...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("\n👋 收到中断信号，守护进程退出")
            break
        except Exception as e:
            log(f"❌ 意外错误: {e}")
            log("等待60秒后重试...")
            time.sleep(60)

if __name__ == "__main__":
    import json  # 在这里导入
    main()
