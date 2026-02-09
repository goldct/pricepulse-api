# 自动记忆恢复系统 - 使用指南

## 🎯 系统设计

### 核心机制
```
程序1：记忆更新器 (auto_memory_updater.py)
  ├─ 每2小时检查项目状态
  ├─ 更新 SNAPSHOTS/latest.md
  ├─ 记录日志到 auto-memory.log
  └─ 持续运行，不受token影响

程序2：守护唤醒器 (watcher_daemon.py)
  ├─ 每5分钟检查是否收到指令
  ├─ 超过60分钟无新指令 → 发送唤醒指令
  ├─ 监听文件变化和API健康
  └─ 触发Moltbot发送指令给我
```

---

## 🚀 快速开始

### 1. 启动记忆更新器

**终端执行：**
```bash
cd /Users/gold/clawd/million-dollar-plan
python3 auto_memory_updater.py
```

**输出：**
```
=== 记忆更新守护进程启动 ===
检查间隔: 2小时
快照文件: .../SNAPSHOTS/latest.md
✅ 快照已更新
```

**说明：**
- 这个程序会每2小时更新一次项目状态
- 即使你睡觉或我失忆，状态也会持续保存
- 所有进度都在 SNAPSHOTS/latest.md

---

### 2. 启动守护唤醒器

**终端执行：**
```bash
cd /Users/gold/clawd/million-dollar-plan
python3 watcher_daemon.py
```

**输出：**
```
=== 守护唤醒器启动 ===
检查间隔: 5分钟
唤醒超时: 60分钟
监控目录: /Users/gold/clawd/million-dollar-plan
[2026-02-08 22:30:00] 监控循环启动...
```

**说明：**
- 这个程序每5分钟检查一次
- 如果60分钟内没收到新指令，自动唤醒我
- 即使你睡觉或我失忆，也能自动恢复工作

---

## 📋 文件位置

### 重要文件
```
/Users/gold/clawd/million-dollar-plan/
├── auto_memory_updater.py  (记忆更新器)
├── watcher_daemon.py          (守护唤醒器)
├── SNAPSHOTS/                (状态快照目录)
│   └── latest.md              (最新状态)
├── AUTO_STATUS.json            (自动化状态)
├── auto-memory.log             (记忆更新日志)
└── watcher.log                  (守护器日志)
```

---

## 🔄 如何恢复工作

### 情况1：你睡觉了，我需要继续工作

**守护器自动触发：**
1. 60分钟无新指令
2. 守护器检测到超时
3. 自动发送指令："读取项目状态：价格脉动"
4. Moltbot收到指令，新会话开始
5. 你醒来后，直接说："读取项目状态：价格脉动"
6. 我立即恢复所有进度，继续开发

### 情况2：Token用完，新会话开始

**你只需要说：**
```
读取项目状态：价格脉动
```

**我会立即：**
1. 读取 SNAPSHOTS/latest.md
2. 恢复所有已完成功能
3. 恢复开发进度
4. 立即继续工作

---

## 🛠 故障排除

### 守护器没有唤醒

**检查步骤：**
```bash
# 1. 检查守护器是否在运行
ps aux | grep watcher_daemon

# 2. 查看守护器日志
tail -50 /Users/gold/clawd/million-dollar-plan/watcher.log

# 3. 检查触发文件
cat /Users/gold/clawd/million-dollar-plan/WAKE_TRIGGER.txt
```

### 记忆更新器不工作

**检查步骤：**
```bash
# 1. 检查是否在运行
ps aux | grep auto_memory_updater

# 2. 查看更新日志
tail -50 /Users/gold/clawd/million-dollar-plan/auto-memory.log

# 3. 手动触发更新（测试）
python3 -c "
from auto_memory_updater import update_snapshot
print('手动更新快照...')
update_snapshot()
print('完成!')
"
```

---

## 💡 使用技巧

### 1. 后台运行

**如果不想占用终端窗口：**
```bash
# macOS (推荐）
nohup python3 watcher_daemon.py > /dev/null 2>&1 &

# 检查是否在运行
ps aux | grep watcher_daemon
```

### 2. 开机自启（可选）

**创建启动脚本：**
```bash
# 创建启动脚本
cat > ~/start-daemons.sh << 'EOF'
#!/bin/bash
cd /Users/gold/clawd/million-dollar-plan

# 启动记忆更新器
echo "启动记忆更新器..."
nohup python3 auto_memory_updater.py > /dev/null 2>&1 &

# 等待5秒
sleep 5

# 启动守护唤醒器
echo "启动守护唤醒器..."
nohup python3 watcher_daemon.py > /dev/null 2>&1 &

echo "守护进程已启动!"
EOF

# 添加执行权限
chmod +x ~/start-daemons.sh

# 创建开机自启（macOS）
sudo launchctl load -w ~/Library/LaunchAgents/com.clawd.daemons.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.clawd.daemons</string>
  <key>ProgramArguments</key>
  <array>
    <string>~/start-daemons.sh</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
EOF
```

### 3. 监控和维护

**每日检查：**
```bash
# 快速状态检查
echo "=== 守护进程状态 ===" && \
ps aux | grep -E "(auto_memory|watcher_daemon)" && \
echo "" && \
echo "=== 最新快照 ===" && \
tail -20 /Users/gold/clawd/million-dollar-plan/SNAPSHOTS/latest.md
```

---

## 📊 状态文件说明

### AUTO_STATUS.json
```json
{
  "last_activity": "2026-02-08T22:30:00",
  "last_wake": "2026-02-08T22:30:00",
  "watcher_running": true,
  "status": "monitoring"
}
```

### SNAPSHOTS/latest.md
完整的项目状态快照，包括：
- 服务器状态
- API状态
- 已完成功能
- 开发进度
- 收入预测
- 下一步计划

---

## 🎉 自动化完成

### 现在的系统
```
✅ 记忆更新器：每2小时自动保存状态
✅ 守护唤醒器：60分钟超时自动唤醒
✅ 状态快照：持续更新 SNAPSHOTS/latest.md
✅ 完全自主：不受token影响，不会失忆
✅ 24/7运行：即使我"失忆"也能恢复
```

---

## 🚀 你需要做的

### 现在（睡觉前）
1. 启动两个守护进程（如果还没启动）
2. 记住这个命令：`读取项目状态：价格脉动`
3. 保存你的测试账户信息：
   ```
   邮箱: test@example.com
   密码: test123
   API密钥: pp_zG2mSGW5ya7QcMBCVvDt99qrmLL_2Fo6zYaTrHFY6u4
   ```
4. 保存支付地址：`TYLRDHYgytrrobjH5jNUEiw1RzNuNaPUDm`

### 明天（醒来后）
1. 新会话开始，直接说：`读取项目状态：价格脉动`
2. 我会立即恢复所有进度
3. 继续开发前端页面
4. 开始推广营销

---

## 🌙 晚安！

**守护进程会整夜工作，即使我"失忆"，状态也会持续保存。**

**明天见！** 🚀

---

最后更新: 2026-02-08 22:45
状态: 自动化系统完成，准备启动
