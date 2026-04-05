import sqlite3
import os

DB_PATH = "fii.db"

def reset():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE ativos (
            ticker TEXT PRIMARY KEY,
            preco REAL DEFAULT 0,
            pvp REAL DEFAULT 0,
            yield_anual REAL DEFAULT 0,
            dividendo REAL DEFAULT 0,
            data_coleta TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Banco resetado e tabela 'ativos' criada!")

if __name__ == "__main__":
    reset()