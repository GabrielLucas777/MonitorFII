import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "investimentos.db"

def salvar_historico(ticker, preco):
    """Insere o preço no banco com ticker padronizado."""
    ticker = ticker.strip().upper()
    data_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO historico (ticker, preco, data_coleta) VALUES (?, ?, ?)", 
                    (ticker, preco, data_agora))
        conn.commit()

def executar_robo():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Busca todos os ativos que você cadastrou
        cursor.execute("SELECT ticker FROM carteira")
        ativos = cursor.fetchall()

    if not ativos:
        print("❌ Ninguém na carteira. Cadastre ativos primeiro.")
        return

    print(f"🤖 Iniciando coleta para {len(ativos)} ativos...")
    for (ticker,) in ativos:
        # SIMULAÇÃO: Substitua pela sua lógica de scraping real
        preco_atual = round(random.uniform(8.5, 11.5), 2)
        salvar_historico(ticker, preco_atual)
        print(f"✅ {ticker.upper()} atualizado: R$ {preco_atual}")

if __name__ == "__main__":
    executar_robo()