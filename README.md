# PricePulse API

Free cryptocurrency price data API for developers.

## Features

- ✅ Real-time prices (BTC, ETH, SOL, and 10+ more)
- ✅ <100ms latency
- ✅ 99.9% uptime
- ✅ Multi-exchange data aggregation (Coinbase, Binance)
- ✅ RESTful API design
- ✅ Free tier available

## Quick Start

### Get All Prices

```bash
curl https://pricepulse.top/api/prices
```

Response:
```json
{
  "count": 10,
  "data": {
    "BTCUSDT": {
      "symbol": "BTCUSDT",
      "price": 70612.0,
      "change_24h": 0,
      "timestamp": "2026-02-08T23:53:24"
    }
  }
}
```

### Get Specific Coin

```bash
curl https://pricepulse.top/api/prices/BTCUSDT
```

### Register for Free API Key

Visit: https://pricepulse.top/register.html

Get higher rate limits with a free API key (300 req/hour → 6,000 req/hour for Basic tier).

## API Endpoints

### Public Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/prices` | GET | Get all prices |
| `/api/prices/{symbol}` | GET | Get specific coin price |
| `/api/health` | GET | API health check |

### Authenticated Endpoints (requires API key)

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | User login |
| `/api/user/profile` | GET | Get user profile |
| `/api/user/regenerate-key` | POST | Regenerate API key |

## Examples

### Python

```python
import requests

# Get all prices
response = requests.get('https://pricepulse.top/api/prices')
data = response.json()

# Get BTC price
btc_price = data['data']['BTCUSDT']['price']
print(f"BTC: ${btc_price:,}")

# With API key
response = requests.get('https://pricepulse.top/api/prices?api_key=YOUR_API_KEY')
data = response.json()
```

### JavaScript

```javascript
// Get all prices
async function getPrices() {
  const response = await fetch('https://pricepulse.top/api/prices');
  const data = await response.json();
  return data.data;
}

// Get BTC price
async function getBTCPrice() {
  const response = await fetch('https://pricepulse.top/api/prices/BTCUSDT');
  const data = await response.json();
  return data.data.price;
}

// Use it
getBTCPrice().then(price => {
  console.log(`BTC: $${price.toLocaleString()}`);
});
```

### Go

```go
package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
)

func main() {
    resp, _ := http.Get("https://pricepulse.top/api/prices")
    defer resp.Body.Close()

    body, _ := ioutil.ReadAll(resp.Body)

    var data map[string]interface{}
    json.Unmarshal(body, &data)

    fmt.Println(data["data"])
}
```

## Pricing

| Plan | Requests/hour | Data Delay | Price |
|------|---------------|------------|-------|
| Free | 300 | 1 hour | ¥0 |
| Basic | 6,000 | Real-time | ¥60/month |
| Pro | 60,000 | Real-time + WebSocket | ¥300/month |

Register: https://pricepulse.top/register.html

## Supported Cryptocurrencies

- BTC (Bitcoin)
- ETH (Ethereum)
- BNB (Binance Coin)
- SOL (Solana)
- XRP (Ripple)
- ADA (Cardano)
- DOGE (Dogecoin)
- MATIC (Polygon)
- LINK (Chainlink)
- DOT (Polkadot)

## Use Cases

- Trading app development
- Data analytics platforms
- Portfolio tracking
- Price alerts
- Algorithmic trading
- DeFi applications

## Data Sources

- Coinbase
- Binance

## Live Demo

- **Website:** https://pricepulse.top
- **API Docs:** https://pricepulse.top/docs
- **Register:** https://pricepulse.top/register.html
- **Login:** https://pricepulse.top/login.html

## License

MIT License - Feel free to use in your projects!

## Contact

- Website: https://pricepulse.top
- Email: contact@pricepulse.top

## Roadmap

- [ ] WebSocket support (Pro tier)
- [ ] Historical data API
- [ ] Price alerts
- [ ] More exchanges
- [ ] More cryptocurrencies
- [ ] Mobile SDKs

---

Built with ❤️ for the crypto community
