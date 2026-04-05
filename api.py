from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import sqlite3
import uvicorn
import re

app = FastAPI()

# --- MÓDULO DE LIMPEZA (REUTILIZÁVEL) ---
def limpar_numerico(valor: str) -> float:
    if not valor or valor in ["-", "N/A", "0,00"]:
        return 0.0
    # Remove R$, %, espaços e pontos de milhar, troca vírgula por ponto
    res = valor.replace('R$', '').replace('%', '').strip()
    if "." in res and "," in res:
        res = res.replace('.', '').replace(',', '.')
    else:
        res = res.replace(',', '.')
    
    res = re.sub(r'[^0-9.-]', '', res)
    try:
        return float(res)
    except ValueError:
        return 0.0

# --- MODELO PYDANTIC COM VALIDAÇÃO ATIVA ---
class RegistroFII(BaseModel):
    ticker: str
    preco: str
    dividendo: str
    pvp: str
    yield_anual: str

    @field_validator('preco', 'dividendo', 'pvp', 'yield_anual', mode='before')
    @classmethod
    def transformar_em_float(cls, v):
        # O Pydantic agora limpa o dado ANTES de validar o modelo
        return str(limpar_numerico(str(v)))

# --- PERSISTÊNCIA ---
def salvar_no_banco(ticker, preco, pvp, yld, div):
    conn = sqlite3.connect("fii.db")
    cursor = conn.cursor()
    try:
        # Forçamos a conversão para float na query para garantir o tipo no SQLite
        cursor.execute("""
            UPDATE ativos 
            SET preco = CAST(? AS REAL), 
                pvp = CAST(? AS REAL), 
                yield_anual = CAST(? AS REAL), 
                dividendo = CAST(? AS REAL), 
                data_coleta = DATETIME('now','localtime')
            WHERE ticker = ?
        """, (preco, pvp, yld, div, ticker.upper()))
        conn.commit()
    finally:
        conn.close()

@app.post("/coleta")
async def endpoint_coleta(ativo: RegistroFII):
    try:
        # Aqui os dados já chegam "limpos" pelo field_validator do Pydantic
        p = float(ativo.preco)
        v = float(ativo.pvp)
        y = float(ativo.yield_anual)
        d = float(ativo.dividendo)

        # Correção de escala para P/VP (ex: 101.0 -> 1.01)
        if v > 50: v /= 100

        salvar_no_banco(ativo.ticker, p, v, y, d)
        
        print(f"✅ [DATA SYNC] {ativo.ticker}: P={p} | V={v} | D={d}")
        return {"status": "sucesso"}
    except Exception as e:
        print(f"❌ Erro na validação/banco: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)