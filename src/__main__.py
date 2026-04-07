"""CLI — orquestrador do fluxo de coleta."""

import argparse
import asyncio
import logging

from .database import init_db, get_all, get_one, upsert, add, delete
from .scraper import scrape, scrape_batch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def cmd_sync(args):
    init_db()
    ativos = get_all()
    if not ativos:
        logging.warning("Nenhum ativo cadastrado.")
        return
    tickers = [a["ticker"] for a in ativos]
    results = asyncio.run(scrape_batch(tickers))
    for r in results:
        upsert(r)
    logging.info("Sync concluido: %d/%d", len(results), len(tickers))


def cmd_sync_one(args):
    init_db()
    t = args.ticker.upper()
    if not get_one(t):
        logging.warning("Ticker %s nao existe.", t)
        return
    res = asyncio.run(scrape(t))
    if res:
        upsert(res)
        logging.info("%s atualizado", t)


def cmd_add(args):
    init_db()
    t = args.ticker.upper()
    if get_one(t):
        logging.warning("%s ja existe.", t)
        return
    add(t)
    logging.info("Coletando dados de %s...", t)
    res = asyncio.run(scrape(t))
    if res:
        upsert(res)
        logging.info("%s adicionado e sincronizado!", t)
    else:
        logging.warning("%s adicionado, mas scraping falhou.", t)


def cmd_list(args):
    init_db()
    ativos = get_all()
    if not ativos:
        print("Nenhum ativo cadastrado.")
        return
    for a in ativos:
        ok = "ok" if a.get("data_coleta") else "pendente"
        print(f"  {a['ticker']:<8} P={a['preco']:<10} V={a['pvp']:<6} Y={a['yield_anual']:<6}% [{ok}]")


def cmd_remove(args):
    delete(args.ticker.upper())
    logging.info("%s removido", args.ticker.upper())


def main():
    p = argparse.ArgumentParser(description="MonitorFII CLI")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("sync")
    s.set_defaults(func=cmd_sync)

    s1 = sub.add_parser("sync-one")
    s1.add_argument("ticker")
    s1.set_defaults(func=cmd_sync_one)

    a = sub.add_parser("add")
    a.add_argument("ticker")
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list")
    l.set_defaults(func=cmd_list)

    r = sub.add_parser("remove")
    r.add_argument("ticker")
    r.set_defaults(func=cmd_remove)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
