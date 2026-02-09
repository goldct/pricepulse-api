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

if api_key != "YOUR_API_KEY":
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
        print("Invalid API key. Please register at https://pricepulse.top/register.html")
else:
    print("Please register at https://pricepulse.top/register.html to get your API key")

# Example 4: Price alert
print("\n=== Example 4: Simple price alert ===")
target_price = 75000

while True:
    response = requests.get(f"{API_BASE}/api/prices/BTCUSDT")
    data = response.json()

    current_price = data['data']['price']
    print(f"BTC: ${current_price:,.2f} (Target: ${target_price:,.2f})")

    if current_price >= target_price:
        print(f"🚀 BTC reached ${target_price:,.2f}!")
        break

    # Check every 60 seconds (free tier limit: 300 req/hour)
    import time
    time.sleep(60)
