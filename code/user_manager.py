#!/usr/bin/env python3
"""
用户管理系统
支持用户注册、登录、API密钥管理
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# 数据库配置
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "users.db"

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UserManager:
    """用户管理器"""

    def __init__(self):
        self.init_db()

    def init_db(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    tier TEXT DEFAULT 'free',
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    api_calls_count INTEGER DEFAULT 0,
                    api_calls_limit INTEGER DEFAULT 300
                )
            ''')

            # API调用日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    endpoint TEXT,
                    status_code INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # 订阅表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    plan TEXT NOT NULL,
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_api_key(self) -> str:
        """生成API密钥"""
        return f"pp_{secrets.token_urlsafe(32)}"

    def register(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """用户注册"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # 检查邮箱是否已存在
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                conn.close()
                return False, "邮箱已注册", None

            # 生成API密钥
            api_key = self.generate_api_key()
            password_hash = self.hash_password(password)

            # 插入用户
            cursor.execute('''
                INSERT INTO users (email, password_hash, api_key)
                VALUES (?, ?, ?)
            ''', (email, password_hash, api_key))

            conn.commit()
            user_id = cursor.lastrowid
            conn.close()

            # 返回用户信息
            user_info = {
                'id': user_id,
                'email': email,
                'api_key': api_key,
                'tier': 'free',
                'created_at': datetime.utcnow().isoformat()
            }

            logger.info(f"用户注册成功: {email}")
            return True, "注册成功", user_info

        except Exception as e:
            logger.error(f"注册失败: {e}")
            return False, str(e), None

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """用户登录"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, email, api_key, tier, status
                FROM users
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))

            user = cursor.fetchone()
            conn.close()

            if not user:
                return False, "邮箱或密码错误", None

            # 检查账户状态
            if user[4] != 'active':
                return False, "账户已被禁用", None

            user_info = {
                'id': user[0],
                'email': user[1],
                'api_key': user[2],
                'tier': user[3],
                'status': user[4]
            }

            # 更新最后登录时间
            self.update_last_login(user[0])

            logger.info(f"用户登录成功: {email}")
            return True, "登录成功", user_info

        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False, str(e), None

    def update_last_login(self, user_id: int):
        """更新最后登录时间"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"更新登录时间失败: {e}")

    def get_user_by_api_key(self, api_key: str) -> Optional[Dict]:
        """通过API密钥获取用户"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, email, tier, api_calls_count, api_calls_limit, status
                FROM users
                WHERE api_key = ?
            ''', (api_key,))

            user = cursor.fetchone()
            conn.close()

            if not user:
                return None

            return {
                'id': user[0],
                'email': user[1],
                'tier': user[2],
                'calls_count': user[3],
                'calls_limit': user[4],
                'status': user[5]
            }
        except Exception as e:
            logger.error(f"通过API密钥获取用户失败: {e}")
            return None

    def check_api_limit(self, user_id: int) -> Tuple[bool, int, int]:
        """检查API调用限制"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT api_calls_count, api_calls_limit
                FROM users
                WHERE id = ?
            ''', (user_id,))

            result = cursor.fetchone()
            conn.close()

            if not result:
                return False, 0, 0

            count, limit = result
            return count < limit, count, limit

        except Exception as e:
            logger.error(f"检查API限制失败: {e}")
            return False, 0, 0

    def increment_api_calls(self, user_id: int) -> bool:
        """增加API调用次数"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE users
                SET api_calls_count = api_calls_count + 1
                WHERE id = ?
            ''', (user_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"增加API调用次数失败: {e}")
            return False

    def reset_api_calls(self):
        """重置API调用次数（每天执行）"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute('UPDATE users SET api_calls_count = 0')

            conn.commit()
            conn.close()
            logger.info("API调用次数已重置")
            return True
        except Exception as e:
            logger.error(f"重置API调用次数失败: {e}")
            return False

    def upgrade_tier(self, user_id: int, new_tier: str) -> bool:
        """升级用户等级"""
        try:
            tier_limits = {
                'free': 300,
                'basic': 6000,
                'pro': 60000
            }

            if new_tier not in tier_limits:
                return False

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # 更新用户等级和限制
            cursor.execute('''
                UPDATE users
                SET tier = ?, api_calls_limit = ?
                WHERE id = ?
            ''', (new_tier, tier_limits[new_tier], user_id))

            # 添加订阅记录
            end_date = datetime.utcnow() + timedelta(days=30)
            cursor.execute('''
                INSERT INTO subscriptions (user_id, plan, end_date, status)
                VALUES (?, ?, ?, 'active')
            ''', (user_id, new_tier, end_date))

            conn.commit()
            conn.close()

            logger.info(f"用户 {user_id} 升级到 {new_tier}")
            return True

        except Exception as e:
            logger.error(f"升级用户等级失败: {e}")
            return False

    def regenerate_api_key(self, user_id: int) -> Optional[str]:
        """重新生成API密钥"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            new_api_key = self.generate_api_key()

            cursor.execute('''
                UPDATE users SET api_key = ? WHERE id = ?
            ''', (new_api_key, user_id))

            conn.commit()
            conn.close()

            logger.info(f"用户 {user_id} API密钥已更新")
            return new_api_key

        except Exception as e:
            logger.error(f"重新生成API密钥失败: {e}")
            return None


# 单例
_user_manager = None

def get_user_manager() -> UserManager:
    """获取用户管理器单例"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager


if __name__ == "__main__":
    # 测试
    manager = get_user_manager()

    # 注册测试用户
    success, message, user = manager.register("test@example.com", "password123")
    print(f"注册: {success}, {message}")
    if user:
        print(f"用户信息: {user}")
        print(f"API密钥: {user['api_key']}")

    # 登录测试
    success, message, user = manager.login("test@example.com", "password123")
    print(f"登录: {success}, {message}")
    if user:
        print(f"用户信息: {user}")
