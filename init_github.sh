#!/bin/bash
# GitHub仓库创建脚本
# 使用前请配置GitHub CLI或使用Web界面创建

echo "=== PricePulse API - GitHub仓库初始化 ==="
echo ""

# 1. 检查是否已安装gh CLI
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI未安装"
    echo "请访问 https://cli.github.com/ 安装"
    echo "或者手动在GitHub Web界面创建仓库"
    exit 1
fi

# 2. 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "⚠️  未登录GitHub"
    echo "请执行: gh auth login"
    exit 1
fi

# 3. 创建仓库
echo "[1/4] 创建GitHub仓库..."
gh repo create pricepulse-api \
    --public \
    --description "Free cryptocurrency price data API" \
    --source=. \
    --remote=origin \
    --push

if [ $? -ne 0 ]; then
    echo "❌ 仓库创建失败"
    exit 1
fi

echo "✅ 仓库创建成功"
echo ""

# 4. 创建必要的文件
echo "[2/4] 创建GitHub配置文件..."

# 创建.github目录
mkdir -p .github/workflows

# 创建README.md
cat > README.md << 'EOF'
# PricePulse API

Free cryptocurrency price data API for developers.

## Features

- ✅ Real-time prices (BTC, ETH, SOL, and 10+ more)
- ✅ <100ms latency
- ✅ RESTful API
- ✅ 99.9% uptime
- ✅ Free tier available

## Quick Start

### Installation

```bash
pip install requests
```

### Usage

```python
import requests

# Get all prices
response = requests.get('https://pricepulse.top/api/prices')
data = response.json()

# Get specific coin
btc_price = data['data']['BTCUSDT']['price']
print(f"BTC: ${btc_price:,}")
```

### With API Key (for higher limits)

```python
import requests

# Register at https://pricepulse.top/register.html to get your API key
response = requests.get('https://pricepulse.top/api/prices?api_key=YOUR_API_KEY')
data = response.json()
```

## API Endpoints

### Get All Prices
```
GET https://pricepulse.top/api/prices
```

### Get Specific Coin
```
GET https://pricepulse.top/api/prices/{symbol}
```

### Get User Profile (requires API key)
```
GET https://pricepulse.top/api/user/profile?api_key=YOUR_API_KEY
```

## Pricing

| Plan | Requests/hour | Data Delay | Price |
|------|---------------|------------|-------|
| Free | 300 | 1 hour | ¥0 |
| Basic | 6,000 | Real-time | ¥60/month |
| Pro | 60,000 | Real-time + WebSocket | ¥300/month |

## Website

- [Main Site](https://pricepulse.top)
- [API Documentation](https://pricepulse.top/docs)
- [Register](https://pricepulse.top/register.html)
- [Login](https://pricepulse.top/login.html)

## License

MIT License

## Contact

- Email: contact@pricepulse.top
- Payment: USDT (TRC20)
EOF

# 创建LICENSE
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 PricePulse

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# 创建.github/workflows/api-test.yml
cat > .github/workflows/api-test.yml << 'EOF'
name: API Health Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Allow manual trigger

jobs:
  check-api:
    runs-on: ubuntu-latest
    steps:
      - name: Check API Health
        run: |
          echo "Checking PricePulse API..."
          response=$(curl -s https://pricepulse.top/api/health)
          echo "API Status: $response"
          
          if echo "$response" | grep -q '"status":"healthy"'; then
            echo "✅ API is healthy"
            exit 0
          else
            echo "❌ API is not healthy"
            exit 1
          fi
EOF

echo "✅ 配置文件创建成功"
echo ""

# 5. 创建示例代码
echo "[3/4] 创建示例代码..."

# 创建examples目录
mkdir -p examples

# 创建Python示例
cat > examples/python_example.py << 'EOF'
#!/usr/bin/env python3
"""
PricePulse API - Python Example
"""

import requests
import json

API_BASE = "https://pricepulse.top"

# Example 1: Get all prices
print("=== Example 1: Get all prices ===")
response = requests.get(f"{API_BASE}/api/prices")
data = response.json()

print(f"Total coins: {data['count']}")
print("\nTop 5 coins:")
for i, (symbol, info) in enumerate(list(data['data'].items())[:5], 1):
    print(f"{i}. {symbol}: ${info['price']:,.2f}")

# Example 2: Get specific coin
print("\n=== Example 2: Get BTC price ===")
response = requests.get(f"{API_BASE}/api/prices/BTCUSDT")
data = response.json()

print(f"BTC: ${data['data']['price']:,.2f}")
print(f"24h Change: {data['data']['change_24h']:.2f}%")

# Example 3: With API key (for higher limits)
print("\n=== Example 3: With API key ===")
# Register at https://pricepulse.top/register.html to get your API key
api_key = "YOUR_API_KEY"

response = requests.get(
    f"{API_BASE}/api/user/profile",
    params={"api_key": api_key}
)

if response.status_code == 200:
    data = response.json()
    print(f"User: {data['data']['email']}")
    print(f"Tier: {data['data']['tier']}")
    print(f"API calls: {data['data']['calls_count']}/{data['data']['calls_limit']}")
else:
    print("Please register to get an API key")
EOF

# 创建JavaScript示例
cat > examples/javascript_example.js << 'EOF'
// PricePulse API - JavaScript Example

const API_BASE = "https://pricepulse.top";

// Example 1: Get all prices
async function getAllPrices() {
  console.log("=== Example 1: Get all prices ===");
  
  const response = await fetch(`${API_BASE}/api/prices`);
  const data = await response.json();
  
  console.log(`Total coins: ${data.count}`);
  console.log("\nTop 5 coins:");
  
  let i = 1;
  for (const [symbol, info] of Object.entries(data.data).slice(0, 5)) {
    console.log(`${i}. ${symbol}: $${info.price.toLocaleString()}`);
    i++;
  }
}

// Example 2: Get specific coin
async function getBTCPrice() {
  console.log("\n=== Example 2: Get BTC price ===");
  
  const response = await fetch(`${API_BASE}/api/prices/BTCUSDT`);
  const data = await response.json();
  
  console.log(`BTC: $${data.data.price.toLocaleString()}`);
  console.log(`24h Change: ${data.data.change_24h}%`);
}

// Example 3: With API key (for higher limits)
async function getUserProfile(apiKey) {
  console.log("\n=== Example 3: With API key ===");
  
  const response = await fetch(
    `${API_BASE}/api/user/profile?api_key=${apiKey}`
  );
  
  if (response.ok) {
    const data = await response.json();
    console.log(`User: ${data.data.email}`);
    console.log(`Tier: ${data.data.tier}`);
    console.log(`API calls: ${data.data.calls_count}/${data.data.calls_limit}`);
  } else {
    console.log("Please register to get an API key");
  }
}

// Run examples
(async () => {
  await getAllPrices();
  await getBTCPrice();
  // Register at https://pricepulse.top/register.html to get your API key
  await getUserProfile("YOUR_API_KEY");
})();
EOF

echo "✅ 示例代码创建成功"
echo ""

# 6. 提交并推送
echo "[4/4] 提交并推送到GitHub..."
git add .
git commit -m "Initial commit: PricePulse API"
git push -u origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "=== ✅ GitHub仓库创建成功 ==="
    echo ""
    echo "仓库地址: https://github.com/YOUR_USERNAME/pricepulse-api"
    echo ""
    echo "下一步:"
    echo "1. 访问仓库地址"
    echo "2. 检查文件是否正确上传"
    echo "3. 更新README中的链接"
    echo "4. 设置GitHub Pages（可选）"
    echo "5. 添加Topics标签"
else
    echo ""
    echo "❌ 推送失败"
    exit 1
fi
