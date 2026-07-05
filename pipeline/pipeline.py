import schedule
import time
from datetime import datetime
from extract import fetch_and_store
from transform import calculate_and_store
from enrich import generate_and_store

TICKERS = ["AAPL", "GOOGL", "MSFT"]

def run_pipeline():
    print(f"\n[{datetime.now()}] Starting StockPulse pipeline...")

    print("\n--- EXTRACT ---")
    for ticker in TICKERS:
        fetch_and_store(ticker)

    print("\n--- TRANSFORM ---")
    for ticker in TICKERS:
        calculate_and_store(ticker)

    print("\n--- ENRICH ---")
    for ticker in TICKERS:
        generate_and_store(ticker)

    print(f"\n[{datetime.now()}] Pipeline complete.")

def main():
    print("StockPulse scheduler started.")
    print("Pipeline will run immediately, then every day at 18:00.\n")

    run_pipeline()

    schedule.every().day.at("18:00").do(run_pipeline)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()