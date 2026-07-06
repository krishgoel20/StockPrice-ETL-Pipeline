import mysql.connector
from groq import Groq
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

def generate_and_store(ticker):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT trade_date, daily_return_pct, moving_avg_7d, volatility
        FROM processed_metrics
        WHERE ticker = %s
        ORDER BY trade_date DESC
        LIMIT 1
    """, (ticker,))

    row = cursor.fetchone()

    if not row:
        print(f"No processed data found for {ticker}")
        return

    cursor.execute("""
        SELECT id FROM ai_insights
        WHERE ticker = %s AND insight_date = %s
    """, (ticker, row["trade_date"]))

    if cursor.fetchone():
        print(f"[{datetime.now()}] {ticker} — Insight already exists, skipping")
        cursor.close()
        conn.close()
        return

    prompt = f"""
    You are a financial analyst. Based on the following stock metrics for {ticker},
    write a concise 2-3 sentence market summary for a data dashboard.

    Date: {row['trade_date']}
    Daily Return: {row['daily_return_pct']}%
    7-Day Moving Average: ${row['moving_avg_7d']}
    Volatility: {row['volatility']}

    Be factual, concise, and professional. No bullet points.
    """

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    summary = response.choices[0].message.content.strip()

    cursor.execute("""
        INSERT INTO ai_insights (ticker, insight_date, summary)
        VALUES (%s, %s, %s)
    """, (
        ticker,
        row["trade_date"],
        summary
    ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[{datetime.now()}] {ticker} — Insight stored")
    print(f"Summary: {summary}\n")

if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL", "MSFT"]
    for ticker in tickers:
        generate_and_store(ticker)