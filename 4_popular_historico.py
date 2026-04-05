import sqlite3
import os
from datetime import datetime, timedelta
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fii.db")

def popular_banco():
    # Ativos com valores base
    ativos_base = {
        "BBIG11": {"preco": 7.20, "div": 0.07, "pvp": 0.88, "yield": 11.5},
        "MXRF11": {"preco": 9.76, "div": 0.10, "pvp": 1.02, "yield": 12.3},
        "VGIA11": {"preco": 9.65, "div": 0.11, "pvp": 0.97, "yield": 13.8}
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # PASSO CRÍTICO: Dropamos a tabela antiga que tinha a trava UNIQUE
    cursor.execute("DROP TABLE IF EXISTS ativos")
    
    # RECRIAÇÃO: Sem o 'UNIQUE' no ticker para permitir o histórico
    cursor.execute('''
        CREATE TABLE ativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT, 
            preco REAL, 
            dividendo REAL, 
            pvp REAL, 
            yield_anual REAL, 
            data_coleta DATETIME
        )
    ''')

    print("🚀 Injetando histórico de 7 dias (agora sem erros)...")

    for dia in range(7, -1, -1):
        # Gera uma data retroativa
        data = (datetime.now() - timedelta(days=dia)).strftime('%Y-%m-%d %H:%M:%S')
        
        for ticker, info in ativos_base.items():
            # Criamos variações reais para o gráfico "vibrar"
            var_preco = random.uniform(-0.15, 0.15)
            var_pvp = random.uniform(-0.02, 0.02)
            
            cursor.execute('''
                INSERT INTO ativos (ticker, preco, dividendo, pvp, yield_anual, data_coleta)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                ticker, 
                round(info["preco"] + var_preco, 2), 
                info["div"], 
                round(info["pvp"] + var_pvp, 2), 
                info["yield"], 
                data
            ))

    conn.commit()
    conn.close()
    print("✅ Banco populado com sucesso! Agora o Dashboard terá dados para os gráficos.")

if __name__ == "__main__":
    popular_banco()