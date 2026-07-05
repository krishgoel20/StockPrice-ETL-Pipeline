# StockPulse 📈
A stock price ETL pipeline with AI-generated market insights.

## What it does
StockPulse is a data engineering pipeline that:
- Extracts daily stock price data for AAPL, GOOGL, and MSFT using yfinance
- Transforms raw prices into meaningful metrics (daily return %, 7-day moving average, volatility)
- Enriches processed data with AI-generated market summaries using Groq API
- Stores all three layers in MySQL (raw → processed → insights)
- Serves the data via FastAPI REST endpoints
- Runs automatically on a daily schedule

## Architecture

```
yfinance API
↓ Extract (extract.py)
MySQL: raw_prices
↓ Transform (transform.py)
MySQL: processed_metrics
↓ Enrich (enrich.py)
MySQL: ai_insights
↓ Serve (api/main.py)
REST API endpoints
```

## Tech Stack
- Python, yfinance, MySQL, Groq API (LLaMA 3.3-70b), FastAPI, schedule

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file with your credentials (see `.env.example`)
5. Run schema: `Get-Content db/schema.sql | mysql -u root -p`
6. Run pipeline: `cd pipeline && python pipeline.py`
7. Start API: `uvicorn api.main:app --reload`

## API Endpoints
| Endpoint | Description |
|---|---|
| `GET /raw/{ticker}` | Raw price data |
| `GET /metrics/{ticker}` | Processed metrics |
| `GET /insights/{ticker}` | AI market summary |

## Limitations
- No idempotency check — running the pipeline multiple times inserts duplicate rows
- Scheduling runs locally only — not deployed to a cloud scheduler
