import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- CONFIGS ---
st.set_page_config(page_title="Sentinel Intelligence", layout="wide")
DB_PATH = Path(__file__).resolve().parent / "investimentos.db"

def carregar_dados(query, params=()):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql(query, conn, params=params)
    except Exception as e:
        st.error(f"Erro no Banco: {e}")
        return pd.DataFrame()

st.title("🛰️ Sentinel Intelligence | Terminal")

# 1. BUSCA ATIVOS
df_ativos = carregar_dados("SELECT DISTINCT UPPER(TRIM(ticker)) as ticker FROM carteira")

if not df_ativos.empty:
    lista_tickers = df_ativos['ticker'].tolist()
    selecionado = st.sidebar.selectbox("🎯 Selecione o Ativo:", lista_tickers)
    
    # 2. BUSCA HISTÓRICO
    df_hist = carregar_dados("""
        SELECT preco, data_coleta FROM historico 
        WHERE UPPER(TRIM(ticker)) = ? 
        ORDER BY data_coleta ASC
    """, (selecionado,))

    if not df_hist.empty:
        # Garantir limpeza total
        df_hist['data_coleta'] = pd.to_datetime(df_hist['data_coleta'])
        df_hist = df_hist.sort_values('data_coleta')

        # MÉTRICAS (Recomendação voltando com tudo)
        atual = float(df_hist['preco'].iloc[-1])
        media = float(df_hist['preco'].mean())
        
        c1, c2 = st.columns(2)
        c1.metric(f"Cotação: {selecionado}", f"R$ {atual:.2f}")
        
        if atual < media:
            c2.success(f"✅ RECOMENDAÇÃO: COMPRA")
            st.info(f"O preço está abaixo da média (R$ {media:.2f}).")
        else:
            c2.warning(f"⚠️ STATUS: AGUARDAR")
            st.info(f"O preço está acima da média (R$ {media:.2f}).")

        # --- VALIDAÇÃO DO GRÁFICO ---
        if len(df_hist) < 2:
            st.warning(f"🚨 Dados insuficientes para gerar o gráfico de {selecionado}.")
            st.write("O banco possui apenas 1 registro. O gráfico precisa de pelo menos 2 pontos para existir.")
            if st.button("Gerar 2º ponto de teste"):
                # Inserção rápida para teste
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("INSERT INTO historico (ticker, preco, data_coleta) VALUES (?, ?, datetime('now'))", (selecionado, atual))
                st.rerun()
        else:
            # --- GRÁFICO DE PONTOS/LINHAS ---
            fig = px.line(df_hist, x='data_coleta', y='preco', markers=True, template="plotly_dark")
            
            fig.update_traces(
                line=dict(color='#00ffcc', width=3),
                marker=dict(size=10, color='#ffffff'),
                texttemplate='R$ %{y:.2f}',
                textposition='top center'
            )
            
            y_min, y_max = df_hist['preco'].min() * 0.98, df_hist['preco'].max() * 1.02
            fig.update_layout(height=450, yaxis=dict(range=[y_min, y_max]))
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"🛑 O ativo {selecionado} não tem NENHUM dado no histórico.")
else:
    st.warning("Cadastre ativos na carteira.")