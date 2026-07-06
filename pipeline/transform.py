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

def calculate_and_store(ticker):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT trade_date, open_price, close_price
        FROM raw_prices
        WHERE ticker = %s
        ORDER BY trade_date ASC
    """, (ticker,))

    rows = cursor.fetchall()

    if len(rows) < 2:
        print(f"Not enough data to transform for {ticker}")
        return

    closes = [row["close_price"] for row in rows]
    inserted = 0
    skipped = 0

    for i, row in enumerate(rows):
        cursor.execute("""
            SELECT id FROM processed_metrics
            WHERE ticker = %s AND trade_date = %s
        """, (ticker, row["trade_date"]))

        if cursor.fetchone():
            skipped += 1
            continue

        daily_return = round(
            ((float(row["close_price"]) - float(row["open_price"])) / float(row["open_price"])) * 100, 4
        )

        window = closes[max(0, i-6):i+1]
        moving_avg = round(sum([float(c) for c in window]) / len(window), 2)

        if len(window) > 1:
            mean = sum([float(c) for c in window]) / len(window)
            variance = sum((float(c) - mean) ** 2 for c in window) / len(window)
            volatility = round(variance ** 0.5, 4)
        else:
            volatility = 0.0

        cursor.execute("""
            INSERT INTO processed_metrics
            (ticker, trade_date, daily_return_pct, moving_avg_7d, volatility)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            ticker,
            row["trade_date"],
            daily_return,
            moving_avg,
            volatility
        ))
        inserted += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[{datetime.now()}] {ticker} — Inserted: {inserted}, Skipped: {skipped}")

if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL", "MSFT"]
    for ticker in tickers:
        calculate_and_store(ticker)