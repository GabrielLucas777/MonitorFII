"""Playwright stealth scraper — extracao StatusInvest."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PwTimeout,
)

from .config import CATEGORIAS, URLS_STATUS, USER_AGENT, SCRAPE_SCRIPT
from .config import NAV_TOUT, WAIT_AFTER_LOAD, DELAY_MIN, DELAY_MAX
from .models import AtivoInput, Ativo

log = logging.getLogger(__name__)

# Scripts injetados ANTES de qualquer pagina carregar
_STEALTH = [
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
    "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});",
    "Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR','pt','en-US','en']});",
    """const _q = window.navigator.permissions.query;
       window.navigator.permissions.query = p =>
         p.name === 'notifications'
           ? Promise.resolve({state: Notification.permission})
           : _q(p);""",
    "window.chrome = {runtime: {}};",
    # Oculta flags de automacao no chrome
    """
    Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});
    """,
]


# ────────────── Context factory ──────────────
async def _launch(pw: Any) -> tuple[Browser, BrowserContext, Page]:
    browser = await pw.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ],
    )
    ctx = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=USER_AGENT,
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
    )
    page = await ctx.new_page()
    for js in _STEALTH:
        await page.add_init_script(js)
    return browser, ctx, page


# ────────────── Single ticker ──────────────
async def scrape(ticker: str) -> Ativo | None:
    async with async_playwright() as pw:
        browser, ctx, page = await _launch(pw)
        result = None
        for cat in CATEGORIAS:
            result = await _try(page, ticker, cat)
            if result:
                break
        await browser.close()
        return result


# ────────────── Batch ──────────────
async def scrape_batch(tickers: list[str]) -> list[Ativo]:
    results: list[Ativo] = []
    async with async_playwright() as pw:
        browser, ctx, page = await _launch(pw)
        for ticker in tickers:
            res = None
            for cat in CATEGORIAS:
                res = await _try(page, ticker, cat)
                if res:
                    break
            if res:
                results.append(res)
            else:
                log.warning("Falha: %s", ticker)
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        await browser.close()
    log.info("Batch: %d/%d sucesso", len(results), len(tickers))
    return results


# ────────────── Internal ──────────────
async def _try(page: Page, ticker: str, cat: str) -> Ativo | None:
    url = URLS_STATUS[cat].format(ticker=ticker.lower())
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=NAV_TOUT)
    except PwTimeout:
        log.debug("Timeout navigate: %s", ticker)
        return None

    try:
        await page.wait_for_selector(
            'div[title="Valor atual do ativo"]',
            timeout=10000,
        )
    except PwTimeout:
        log.debug("Timeout selector: %s (%s)", ticker, cat)
        return None

    await asyncio.sleep(WAIT_AFTER_LOAD)

    raw = await page.evaluate(SCRAPE_SCRIPT)
    if not raw or raw.get("preco") is None:
        log.debug("Dados vazios: %s (%s)", ticker, cat)
        return None

    try:
        raw_model = AtivoInput(ticker=ticker, **raw)
        return Ativo(
            ticker=raw_model.ticker,
            preco=raw_model.preco,
            pvp=raw_model.pvp,
            yield_anual=raw_model.yld,
            dividendo=raw_model.div,
        )
    except Exception:
        log.exception("Validacao falhou: %s", ticker)
        return None
