"""Playwright stealth scraper para StatusInvest."""

from __future__ import annotations

import asyncio
import logging
import random

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout

from .config import (
    CATEGORIAS,
    NAVIGATION_TIMEOUT,
    WAIT_AFTER_LOAD,
    MIN_DELAY_BETWEEN_REQUESTS,
    MAX_DELAY_BETWEEN_REQUESTS,
    SCRAPE_SCRIPT,
    URLS_STATUS,
    USER_AGENT,
)
from .models import AtivoRaw, AtivoCleaned

log = logging.getLogger(__name__)

STEALTH_SCRIPTS = [
    # Remove webdriver flag
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
    # Patch plugins to look like real Chrome
    """
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });
    """,
    # Spoof languages
    "Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});",
    # Mock permissions query
    """
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({state: Notification.permission}) :
            originalQuery(parameters)
    );
    """,
    # Override chrome runtime
    """
    window.chrome = {runtime: {}};
    """
]


async def apply_stealth(page: Page) -> None:
    for script in STEALTH_SCRIPTS:
        await page.add_init_script(script)


async def scrape_ticker(ticker: str) -> AtivoCleaned | None:
    """Tenta extrair dados de um ticker em todas as categorias disponiveis."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=USER_AGENT,
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )
        page = await context.new_page()
        await apply_stealth(page)

        result = None
        for categoria in CATEGORIAS:
            result = await _try_extract(page, ticker, categoria)
            if result:
                break

        await browser.close()
        return result


async def scrape_batch(tickers: list[str]) -> list[AtivoCleaned]:
    """Coleta dados de multiplos tickers com delays anti-ban."""
    resultados: list[AtivoCleaned] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=USER_AGENT,
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )
        page = await context.new_page()
        await apply_stealth(page)

        for ticker in tickers:
            log.info("Coletando: %s (%d restantes)", ticker, len(tickers) - resultados.__len__() - 1)
            result = None
            for categoria in CATEGORIAS:
                result = await _try_extract(page, ticker, categoria)
                if result:
                    break
            if result:
                resultados.append(result)
            else:
                log.warning("Falha ao coletar dados de %s", ticker)
            # Delay randomico anti-ban
            await asyncio.sleep(random.uniform(MIN_DELAY_BETWEEN_REQUESTS, MAX_DELAY_BETWEEN_REQUESTS))

        await browser.close()

    log.info("Coleta finalizada: %d/%d sucesso", len(resultados), len(tickers))
    return resultados


async def _try_extract(page: Page, ticker: str, categoria: str) -> AtivoCleaned | None:
    url = URLS_STATUS[categoria].format(ticker=ticker.lower())
    log.debug("Acessando: %s", url)

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT)

        # Aguarda conteudo renderizar (espera por elementos chave)
        try:
            await page.wait_for_selector(
                'div[title="Valor atual do ativo"]',
                timeout=10000,
            )
        except PlaywrightTimeout:
            log.warning("Timeout - elemento principal nao encontrado para %s", ticker)
            return None

        # Extracao via JS injection
        raw = await page.evaluate(SCRAPE_SCRIPT)

        if not raw or raw.get("preco") is None:
            log.warning("Pagina vazia para %s (%s)", ticker, categoria)
            return None

        # Valida com Pydantic
        raw_model = AtivoRaw(ticker=ticker, **raw)
        cleaned = AtivoCleaned(
            ticker=raw_model.ticker,
            preco=raw_model.preco,
            pvp=raw_model.pvp,
            yield_anual=raw_model.yld,
            dividendo=raw_model.div,
        )

        return cleaned

    except PlaywrightTimeout:
        log.warning("Timeout de navegacao para %s (%s)", ticker, categoria)
        return None
    except Exception:
        log.exception("Erro inesperado ao coletar %s (%s)", ticker, categoria)
        return None
