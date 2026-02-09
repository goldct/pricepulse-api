#!/usr/bin/env python3
"""
加密货币数据API服务
提供RESTful API接口，供客户端调用
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
from typing import List, Dict, Optional
import os
import json
from pathlib import Path
import asyncio
from crypto_collector import CryptoPriceCollector
from user_manager import get_user_manager
from pydantic import BaseModel

app = FastAPI(
    title="Crypto Price API",
    description="实时加密货币价格数据API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据采集器
collector = CryptoPriceCollector()

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 当前价格数据（内存缓存）
current_prices: Dict = {}

# 后台任务：持续采集
async def background_collector():
    """后台持续采集数据"""
    while True:
        try:
            data = await collector.collect_all()
            if data:
                current_prices.update(data)
                collector.save_to_file(data)
        except Exception as e:
            print(f"Background collector error: {e}")

        await asyncio.sleep(30)  # 每30秒采集一次


@app.on_event("startup")
async def startup_event():
    """启动时开始采集"""
    # 启动后台采集任务
    asyncio.create_task(background_collector())


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Crypto Price API",
        "version": "1.0.0",
        "endpoints": {
            "/api/prices": "获取所有价格",
            "/api/prices/{symbol}": "获取指定币种价格",
            "/api/history": "获取历史数据",
            "/api/stats": "统计信息"
        }
    }


@app.get("/api/prices")
async def get_all_prices():
    """获取所有币种价格"""
    if not current_prices:
        raise HTTPException(status_code=503, detail="数据初始化中，请稍后")

    return {
        "count": len(current_prices),
        "data": current_prices,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/prices/{symbol}")
async def get_price(symbol: str):
    """获取指定币种价格"""
    symbol = symbol.upper()

    if not current_prices:
        raise HTTPException(status_code=503, detail="数据初始化中，请稍后")

    if symbol not in current_prices:
        raise HTTPException(status_code=404, detail=f"未找到币种: {symbol}")

    return {
        "symbol": symbol,
        "data": current_prices[symbol],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/history")
async def get_history(limit: int = 10):
    """获取历史数据"""
    try:
        # 读取最新的数据文件
        files = sorted(DATA_DIR.glob("prices_*.json"), reverse=True)[:limit]

        history = []
        for file_path in files:
            with open(file_path, 'r') as f:
                data = json.load(f)
                history.append(data)

        return {
            "count": len(history),
            "data": history
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取历史数据失败: {e}")


@app.get("/api/stats")
async def get_stats():
    """获取统计信息"""
    if not current_prices:
        raise HTTPException(status_code=503, detail="数据初始化中，请稍后")

    # 计算一些统计信息
    prices = [data['price'] for data in current_prices.values()]
    volumes = [data.get('volume', 0) for data in current_prices.values()]

    return {
        "total_symbols": len(current_prices),
        "price_range": {
            "min": min(prices),
            "max": max(prices)
        },
        "total_volume": sum(volumes),
        "last_update": collector.last_update.isoformat() if collector.last_update else None,
        "uptime": "运行中"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "collector_running": collector.last_update is not None,
        "data_count": len(current_prices)
    }


# ===== 用户管理API =====

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """用户注册"""
    user_manager = get_user_manager()

    # 验证邮箱格式
    if "@" not in request.email or "." not in request.email:
        raise HTTPException(status_code=400, detail="邮箱格式不正确")

    # 验证密码长度
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6位")

    success, message, user = user_manager.register(
        request.email,
        request.password
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "data": {
            "user_id": user['id'],
            "email": user['email'],
            "api_key": user['api_key'],
            "tier": user['tier']
        }
    }


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """用户登录"""
    user_manager = get_user_manager()

    success, message, user = user_manager.login(
        request.email,
        request.password
    )

    if not success:
        raise HTTPException(status_code=401, detail=message)

    return {
        "success": True,
        "message": message,
        "data": {
            "user_id": user['id'],
            "email": user['email'],
            "api_key": user['api_key'],
            "tier": user['tier']
        }
    }


@app.get("/api/user/profile")
async def get_user_profile(api_key: str):
    """获取用户资料"""
    user_manager = get_user_manager()

    user = user_manager.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="API密钥无效")

    return {
        "success": True,
        "data": user
    }


@app.post("/api/user/regenerate-key")
async def regenerate_api_key(api_key: str):
    """重新生成API密钥"""
    user_manager = get_user_manager()

    user = user_manager.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="API密钥无效")

    new_key = user_manager.regenerate_api_key(user['id'])
    if not new_key:
        raise HTTPException(status_code=500, detail="生成新密钥失败")

    return {
        "success": True,
        "message": "API密钥已更新",
        "data": {
            "api_key": new_key
        }
    }


@app.get("/api/user/api-usage")
async def get_api_usage(api_key: str):
    """获取API使用情况"""
    user_manager = get_user_manager()

    user = user_manager.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="API密钥无效")

    return {
        "success": True,
        "data": {
            "calls_count": user['calls_count'],
            "calls_limit": user['calls_limit'],
            "percentage": (user['calls_count'] / user['calls_limit']) * 100
        }
    }


if __name__ == "__main__":
    # 启动API服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
