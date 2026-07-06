import yfinance as yf
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def fetch_and_store(ticker, period="5d"):
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    inserted = 0
    skipped = 0

    for date, row in df.iterrows():
        cursor.execute("""
            SELECT id FROM raw_prices
            WHERE ticker = %s AND trade_date = %s
        """, (ticker, date.date()))

        if cursor.fetchone():
            skipped += 1
            continue

        cursor.execute("""
            INSERT INTO raw_prices
            (ticker, trade_date, open_price, high_price, low_price, close_price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            ticker,
            date.date(),
            round(float(row["Open"]), 2),
            round(float(row["High"]), 2),
            round(float(row["Low"]), 2),
            round(float(row["Close"]), 2),
            int(row["Volume"])
        ))
        inserted += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[{datetime.now()}] {ticker} — Inserted: {inserted}, Skipped: {skipped}")

if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL", "MSFT"]
    for ticker in tickers:
        fetch_and_store(ticker)