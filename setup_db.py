import sqlite3

def setup():
    conn = sqlite3.connect('fii.db')
    cursor = conn.cursor()
    # Deleta para recriar do zero e evitar conflito de colunas
    cursor.execute('DROP TABLE IF EXISTS ativos')
    cursor.execute('''
        CREATE TABLE ativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            preco REAL,
            dividendo REAL,
            pvp REAL,
            yield_anual REAL,
            data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Banco de dados 'fii.db' configurado com sucesso!")

if __name__ == "__main__":
    setup()