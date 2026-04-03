import sqlite3
import random
import time
import pandas as pd
from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path

# --- CONFIGURAÇÕES DE AMBIENTE ---
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "investimentos.db"

# User-Agents para evitar bloqueios básicos
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

def buscar_ativos_no_banco():
    """Lê os tickers diretamente da tabela 'carteira'."""
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            # Conforme nosso diagnóstico, a tabela correta é 'carteira'
            df = pd.read_sql("SELECT DISTINCT ticker FROM carteira", conn)
            if df.empty:
                return []
            return [t.upper() for t in df['ticker'].tolist()]
    except Exception as e:
        print(f"❌ Erro ao acessar a tabela 'carteira': {e}")
        return []

def realizar_scrap_status_invest(ticker):
    """Executa o scrap no StatusInvest com tratamento de erros e camuflagem."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        # Injeção para esconder o rastro de automação básica
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            url = f"https://statusinvest.com.br/fundos-imobiliarios/{ticker.lower()}"
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            
            # Seletor robusto para o valor atual
            seletor_valor = 'div[title="Valor atual do ativo"] strong.value'
            page.wait_for_selector(seletor_valor, timeout=10000)
            
            valor_raw = page.inner_text(seletor_valor)
            # Limpeza técnica: remove pontos de milhar e troca vírgula por ponto
            valor_limpo = float(valor_raw.replace(".", "").replace(",", ".").strip())
            return valor_limpo
            
        except Exception as e:
            print(f"⚠️ Falha ao processar {ticker}: {e}")
            return None
        finally:
            browser.close()

def salvar_historico(ticker, preco):
    """Persiste o dado coletado no banco de dados."""
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("""
                INSERT INTO historico (ticker, preco, data_coleta) 
                VALUES (?, ?, ?)
            """, (ticker, preco, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")

def processar_varredura(ativos):
    """Gerencia o fluxo de trabalho do robô."""
    total = len(ativos)
    print(f"\n🚀 SENTINEL RPA | INICIANDO COLETA DE {total} ATIVOS")
    print("-" * 50)

    for i, ativo in enumerate(ativos, 1):
        hoje = datetime.now().strftime('%Y-%m-%d')
        
        # 1. Validação de Idempotência (Pular se já existir registro hoje)
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM historico WHERE ticker = ? AND data_coleta LIKE ?", (ativo, f"{hoje}%"))
            if cursor.fetchone():
                print(f"[{i}/{total}] ✅ {ativo:<8} | JÁ ESTÁ ATUALIZADO")
                continue
        
        # 2. Execução do Scrap
        print(f"[{i}/{total}] 🔍 Coletando {ativo}...", end="\r")
        preco = realizar_scrap_status_invest(ativo)
        
        if preco:
            salvar_historico(ativo, preco)
            print(f"[{i}/{total}] 💾 {ativo:<8} | SUCESSO: R$ {preco:.2f}")
            # Delay