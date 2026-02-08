from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from typing import List
import asyncio
import uvicorn

from app.services import get_price, check_alerts
from app.models import PriceResponse, AlertRequest
from app.db import SessionLocal, HistoricalPrice, PriceAlert

app = FastAPI(title="Stock / Crypto Price Tracker")


@app.on_event("startup")
async def start_alert_loop():
    async def loop():
        while True:
            await check_alerts()
            await asyncio.sleep(30)
    try:
        asyncio.create_task(loop())
    except Exception as e:
        print("Startup loop error:", e)


@app.get("/price/{symbol}", response_model=PriceResponse)
async def price(symbol: str, currency: str = Query("usd")):
    data = await get_price(symbol, currency)
    if not data:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return data


@app.get("/history/{symbol}", response_model=List[PriceResponse])
def history(symbol: str, currency: str = "usd", limit: int = 10):
    db = SessionLocal()
    try:
        records = (
            db.query(HistoricalPrice)
            .filter(HistoricalPrice.symbol == symbol.upper())
            .order_by(HistoricalPrice.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            PriceResponse(symbol=r.symbol, price=r.price, timestamp=r.timestamp)
            for r in records
        ]
    finally:
        db.close()


@app.post("/alerts")
def create_alert(alert: AlertRequest, bg: BackgroundTasks):
    db = SessionLocal()
    try:
        new_alert = PriceAlert(
            symbol=alert.symbol.upper(),
            currency=alert.currency.lower(),
            target_price=alert.target_price,
            email=alert.email
        )
        db.add(new_alert)
        db.commit()
    finally:
        db.close()

    bg.add_task(check_alerts)
    return {"message": "Alert created"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )