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
    console.log("Please register at https://pricepulse.top/register.html");
  }
}

// Example 4: Price monitoring
async function monitorPrice(targetPrice) {
  console.log(`\n=== Example 4: Monitor BTC price (Target: $${targetPrice.toLocaleString()}) ===`);

  while (true) {
    const response = await fetch(`${API_BASE}/api/prices/BTCUSDT`);
    const data = await response.json();

    const currentPrice = data.data.price;
    console.log(`BTC: $${currentPrice.toLocaleString()}`);

    if (currentPrice >= targetPrice) {
      console.log(`🚀 BTC reached $${targetPrice.toLocaleString()}!`);
      break;
    }

    // Check every 60 seconds (free tier limit: 300 req/hour)
    await new Promise(resolve => setTimeout(resolve, 60000));
  }
}

// Example 5: Simple price display (for web pages)
async function displayPrices() {
  console.log("\n=== Example 5: Simple price display ===");

  const response = await fetch(`${API_BASE}/api/prices`);
  const data = await response.json();

  const topCoins = Object.entries(data.data).slice(0, 5);

  let html = "<ul>";
  for (const [symbol, info] of topCoins) {
    html += `<li>${symbol}: $${info.price.toLocaleString()}</li>`;
  }
  html += "</ul>";

  console.log("HTML for web pages:");
  console.log(html);
}

// Run examples
(async () => {
  await getAllPrices();
  await getBTCPrice();

  // Register at https://pricepulse.top/register.html to get your API key
  // await getUserProfile("YOUR_API_KEY");

  // Monitor if BTC reaches $75,000
  // await monitorPrice(75000);

  // Display prices for web pages
  // await displayPrices();
})();
