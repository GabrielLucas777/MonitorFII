"""CLI isolado p/ scraping — chamado pelo dashboard via subprocess."""
import asyncio
import json
import sys
import logging

logging.disable(logging.WARNING)

from src.database import init_db, get_all, upsert
from src.scraper import scrape, scrape_batch


def scrape_one(ticker: str):
    init_db()
    res = asyncio.run(scrape(ticker.upper()))
    if res:
        upsert(res)
        print(json.dumps({"status": "ok", "data": res.to_dict()}))
    else:
        print(json.dumps({"status": "fail"}))


def scrape_all():
    init_db()
    ativos = get_all()
    if not ativos:
        print(json.dumps({"status": "empty"}))
        return
    tickers = [a["ticker"] for a in ativos]
    results = asyncio.run(scrape_batch(tickers))
    for r in results:
        upsert(r)
    print(json.dumps({"status": "done", "count": len(results), "total": len(tickers)}))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "usage", "help": "pip install run_scraper.py <ticker|all>"}))
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "all":
        scrape_all()
    else:
        scrape_one(cmd)
