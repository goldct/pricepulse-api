#!/usr/bin/env python3
"""
加密货币价格数据采集器
实时采集多个交易所的加密货币价格数据
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

# 配置日志
import os
log_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'collector.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CryptoPriceCollector:
    """加密货币价格采集器"""

    def __init__(self):
        self.prices: Dict[str, float] = {}
        self.volume: Dict[str, float] = {}
        self.change_24h: Dict[str, float] = {}
        self.last_update: Optional[datetime] = None

        # 支持的交易所API
        self.exchanges = {
            'binance': 'https://api.binance.com/api/v3',
            'coinbase': 'https://api.coinbase.com/v2',
            'kraken': 'https://api.kraken.com/0/public',
            'huobi': 'https://api.huobi.pro'
        }

        # 重点关注的交易对
        self.symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
            'ADAUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'LINKUSDT'
        ]

    async def fetch_binance_ticker(self) -> Dict:
        """获取Binance价格"""
        try:
            url = f"{self.exchanges['binance']}/ticker/24hr"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()

                    # 确保返回的是列表
                    if not isinstance(data, list):
                        logger.error(f"Binance返回格式错误: {type(data)}")
                        return {}

                    result = {}
                    for item in data:
                        try:
                            symbol = item.get('symbol')
                            if symbol and symbol in self.symbols:
                                result[symbol] = {
                                    'exchange': 'binance',
                                    'symbol': symbol,
                                    'price': float(item.get('lastPrice', 0)),
                                    'volume': float(item.get('volume', 0)),
                                    'change_24h': float(item.get('priceChangePercent', 0)),
                                    'timestamp': datetime.utcnow().isoformat()
                                }
                        except Exception as e:
                            logger.warning(f"处理Binance数据项失败: {e}")
                            continue

                    logger.info(f"Binance: 获取到 {len(result)} 个交易对数据")
                    return result

        except Exception as e:
            logger.error(f"Binance采集失败: {e}")
            return {}

    async def fetch_coinbase_price(self) -> Dict:
        """获取Coinbase价格"""
        try:
            # 转换交易对格式
            symbol_map = {
                'BTCUSDT': 'BTC-USD',
                'ETHUSDT': 'ETH-USD',
                'SOLUSDT': 'SOL-USD',
                'XRPUSDT': 'XRP-USD',
                'ADAUSDT': 'ADA-USD',
                'DOGEUSDT': 'DOGE-USD',
                'MATICUSDT': 'MATIC-USD'
            }

            result = {}
            async with aiohttp.ClientSession() as session:
                for symbol, coinbase_symbol in symbol_map.items():
                    try:
                        url = f"{self.exchanges['coinbase']}/prices/{coinbase_symbol}/spot"
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            data = await response.json()
                            if 'data' in data and 'amount' in data['data']:
                                result[symbol] = {
                                    'exchange': 'coinbase',
                                    'symbol': symbol,
                                    'price': float(data['data']['amount']),
                                    'volume': 0,
                                    'change_24h': 0,
                                    'timestamp': datetime.utcnow().isoformat()
                                }
                                logger.info(f"Coinbase {symbol}: {result[symbol]['price']}")
                    except Exception as e:
                        logger.warning(f"Coinbase {coinbase_symbol} 采集失败: {e}")
                        continue

            logger.info(f"Coinbase: 获取到 {len(result)} 个交易对数据")
            return result

        except Exception as e:
            logger.error(f"Coinbase采集失败: {e}")
            return {}

    async def collect_all(self) -> Dict:
        """采集所有交易所数据"""
        tasks = [
            self.fetch_binance_ticker(),
            self.fetch_coinbase_price()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        all_data = {}
        for result in results:
            if isinstance(result, dict):
                all_data.update(result)

        # 计算平均价格（如果多个交易所有数据）
        aggregated = self._aggregate_prices(all_data)

        self.last_update = datetime.utcnow()
        return aggregated

    def _aggregate_prices(self, raw_data: Dict) -> Dict:
        """聚合多个交易所的价格"""
        aggregated = {}

        for symbol, data in raw_data.items():
            if symbol not in aggregated:
                aggregated[symbol] = {
                    'symbol': symbol,
                    'exchanges': [],
                    'price': data.get('price'),
                    'volume': data.get('volume', 0),
                    'change_24h': data.get('change_24h', 0),
                    'timestamp': data.get('timestamp')
                }

            aggregated[symbol]['exchanges'].append(data['exchange'])

        return aggregated

    def save_to_file(self, data: Dict):
        """保存数据到文件"""
        filepath = f"/Users/gold/clawd/million-dollar-plan/data/prices_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"数据已保存到: {filepath}")

        except Exception as e:
            logger.error(f"保存数据失败: {e}")

    async def run_once(self):
        """运行一次采集"""
        logger.info("开始数据采集...")
        data = await self.collect_all()

        if data:
            self.save_to_file(data)

            # 打印最新价格
            logger.info("\n=== 最新价格 ===")
            for symbol, info in sorted(data.items())[:5]:  # 只显示前5个
                logger.info(f"{symbol}: ${info['price']:.2f} ({info.get('change_24h', 0):.2f}%)")

            logger.info(f"更新时间: {self.last_update}")
        else:
            logger.warning("未获取到任何数据")

        return data

    async def run_continuous(self, interval_seconds: int = 30):
        """持续采集"""
        logger.info(f"启动持续采集，间隔 {interval_seconds} 秒")

        while True:
            try:
                await self.run_once()
                await asyncio.sleep(interval_seconds)

            except KeyboardInterrupt:
                logger.info("停止采集")
                break
            except Exception as e:
                logger.error(f"采集出错: {e}")
                await asyncio.sleep(5)  # 出错后等待5秒重试


async def main():
    """主函数"""
    collector = CryptoPriceCollector()

    # 运行一次采集
    await collector.run_once()

    # 如果需要持续运行，取消下面注释
    # await collector.run_continuous(interval_seconds=30)


if __name__ == '__main__':
    asyncio.run(main())
