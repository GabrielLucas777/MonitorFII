import asyncio
import sqlite3
import os
import random
import re
import sys
from datetime import datetime
from playwright.async_api import async_playwright

DB_PATH = "fii.db"

def inicializar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Cria a tabela base se nao existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ativos (
            ticker TEXT PRIMARY KEY,
            preco REAL DEFAULT 0,
            pvp REAL DEFAULT 0,
            yield_anual REAL DEFAULT 0,
            dividendo REAL DEFAULT 0,
            quantidade INTEGER DEFAULT 0,
            custo_medio REAL DEFAULT 0,
            data_coleta TEXT
        )
    """)
    # Migracao automatica: adiciona colunas se o banco for antigo
    cursor.execute("PRAGMA table_info(ativos)")
    colunas = [col[1] for col in cursor.fetchall()]
    if 'quantidade' not in colunas:
        cursor.execute("ALTER TABLE ativos ADD COLUMN quantidade INTEGER DEFAULT 0")
    if 'custo_medio' not in colunas:
        cursor.execute("ALTER TABLE ativos ADD COLUMN custo_medio REAL DEFAULT 0")
    
    conn.commit()
    conn.close()

def salvar_no_banco(dados):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        def limpar(v): 
            if not v or "---" in v: return 0.0
            num = re.sub(r'[^\d.,]', '', str(v))
            if not num: return 0.0
            return float(num.replace('.', '').replace(',', '.').strip())
        
        cursor.execute("""
            UPDATE ativos 
            SET preco = ?, pvp = ?, yield_anual = ?, dividendo = ?, data_coleta = ?
            WHERE ticker = ?
        """, (limpar(dados['preco']), limpar(dados['pvp']), limpar(dados['yld']), 
              limpar(dados['div']), datetime.now().strftime("%d/%m/%Y %H:%M"), dados['ticker']))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro SQLite: {e}")
        return False

async def extrair_dados_v3(page, ticker, categoria):
    url = f"https://statusinvest.com.br/{categoria}/{ticker.lower()}"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        dados = await page.evaluate("""
            () => {
                const buscarPorTexto = (label) => {
                    const elementos = document.querySelectorAll('.item, .info, .sub-value');
                    for (let el of elementos) {
                        if ((el.innerText || "").toUpperCase().includes(label.toUpperCase())) {
                            const valorEl = el.querySelector('strong, .value');
                            return valorEl ? valorEl.innerText : "---";
                        }
                    }
                    return "---";
                };
                return {
                    preco: document.querySelector('div[title="Valor atual do ativo"] strong')?.innerText || "---",
                    pvp: buscarPorTexto('P/VP'),
                    yld: buscarPorTexto('Dividend Yield'),
                    div: document.querySelector('#dy-info strong')?.innerText || "0,00"
                };
            }
        """)
        return {"ticker": ticker, "preco": dados['preco'], "pvp": dados['pvp'], "yld": dados['yld'], "div": dados['div']} if dados['preco'] != "---" else None
    except: return None

async def executar():
    inicializar_banco()
    conn = sqlite3.connect(DB_PATH)
    ativos = [t[0] for t in conn.execute("SELECT ticker FROM ativos").fetchall()]
    conn.close()
    if not ativos: return
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        page = await context.new_page()
        for ticker in ativos:
            print(f"Sincronizando: {ticker}")
            res = await extrair_dados_v3(page, ticker, "fundos-imobiliarios")
            if not res: res = await extrair_dados_v3(page, ticker, "fiagros")
            if res: salvar_no_banco(res)
            await asyncio.sleep(random.uniform(5, 7))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(executar())