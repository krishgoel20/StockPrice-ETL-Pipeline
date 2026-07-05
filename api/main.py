from fastapi import FastAPI, HTTPException
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="StockPulse API")

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.get("/")
def root():
    return {"message": "StockPulse API is running"}

@app.get("/raw/{ticker}")
def get_raw_prices(ticker: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM raw_prices
        WHERE ticker = %s
        ORDER BY trade_date DESC
    """, (ticker.upper(),))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
    return {"ticker": ticker.upper(), "data": rows}

@app.get("/metrics/{ticker}")
def get_metrics(ticker: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM processed_metrics
        WHERE ticker = %s
        ORDER BY trade_date DESC
    """, (ticker.upper(),))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No metrics found for {ticker}")
    return {"ticker": ticker.upper(), "metrics": rows}

@app.get("/insights/{ticker}")
def get_insights(ticker: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM ai_insights
        WHERE ticker = %s
        ORDER BY insight_date DESC
        LIMIT 1
    """, (ticker.upper(),))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"No insights found for {ticker}")
    return {"ticker": ticker.upper(), "insight": row}