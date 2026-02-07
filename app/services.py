import httpx
import json
from datetime import datetime
from app.redis_client import redis_get, redis_setex
from app.db import SessionLocal, HistoricalPrice, PriceAlert

STOCK_API_URL = "https://api.coingecko.com/api/v3/simple/price"


def save_price(symbol: str, currency: str, price: float, timestamp: datetime):
    db = SessionLocal()
    try:
        record = HistoricalPrice(
            symbol=symbol.upper(),
            currency=currency.lower(),
            price=price,
            timestamp=timestamp
        )
        db.add(record)
        db.commit()
    finally:
        db.close()


async def get_price(symbol: str, currency: str = "usd"):
    symbol = symbol.lower()
    currency = currency.lower()
    cache_key = f"{symbol}:{currency}"

    cached = redis_get(cache_key)
    if cached:
        return json.loads(cached)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                STOCK_API_URL,
                params={"ids": symbol, "vs_currencies": currency}
            )
            resp.raise_for_status()
            result = resp.json()
    except Exception as e:
        print("API fetch error:", e)
        return None

    price = result.get(symbol, {}).get(currency)
    if price is None:
        return None

    timestamp = datetime.utcnow()
    data = {
        "symbol": symbol.upper(),
        "price": price,
        "timestamp": timestamp.isoformat()
    }

    # Save Redis safely
    try:
        redis_setex(cache_key, 30, json.dumps(data))
    except Exception as e:
        print("Redis save failed:", e)

    # Save DB
    save_price(symbol, currency, price, timestamp)

    return data


async def check_alerts():
    db = SessionLocal()
    try:
        alerts = db.query(PriceAlert).filter(PriceAlert.triggered == 0).all()
        for alert in alerts:
            data = await get_price(alert.symbol, alert.currency)
            if not data:
                continue
            if data["price"] >= alert.target_price:
                print(f"ALERT: {alert.symbol} hit {data['price']} (target {alert.target_price})")
                alert.triggered = 1
                db.commit()
    finally:
        db.close()
