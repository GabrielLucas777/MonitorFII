import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fii.db")

def resetar_zerados():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Define a data_coleta como NULL para quem não tem preço
    # Isso engana o robô fazendo ele achar que o ativo nunca foi coletado
    cursor.execute("UPDATE ativos SET data_coleta = NULL WHERE preco = 0 OR preco IS NULL")
    conn.commit()
    print(f"✅ {cursor.rowcount} ativos resetados. Pode rodar o robô agora!")
    conn.close()

if __name__ == "__main__":
    resetar_zerados()