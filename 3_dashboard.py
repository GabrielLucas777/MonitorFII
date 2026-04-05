import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import subprocess
import sys
import time

# Configuração da Página
st.set_page_config(page_title="MonitorFII | monitorador de Ativos", layout="wide", initial_sidebar_state="expanded")

# CSS para interface Sênior e Padronização de Cores
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00d4ff !important; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; }
    
    /* Classes de Status Padronizadas */
    .status-box { border-left: 5px solid; padding: 12px 20px; border-radius: 4px; margin-bottom: 25px; font-size: 0.95rem; }
    .status-oportunidade { border-color: #10B981; background-color: #064E3B; color: #D1FAE5; }
    .status-caro { border-color: #EF4444; background-color: #451A1A; color: #FEE2E2; }
    .status-neutro { border-color: #3B82F6; background-color: #1E3A8A; color: #DBEAFE; }
    .status-aguardando { border-color: #6B7280; background-color: #374151; color: #F3F4F6; }
    </style>
""", unsafe_allow_html=True)

DB_PATH = "fii.db"
ROBO_SCRIPT = "2_robo.py"

def carregar_dados():
    if not os.path.exists(DB_PATH): 
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS ativos (ticker TEXT PRIMARY KEY, preco REAL, pvp REAL, yield_anual REAL, dividendo REAL, data_coleta TEXT)")
    df = pd.read_sql_query("SELECT * FROM ativos", conn)
    conn.close()
    for col in ['preco', 'pvp', 'yield_anual', 'dividendo']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df

# ==========================================
# LADO ESQUERDO: CONTROLES (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title(" Painel de Controle")
    st.markdown("### Configurações de Ativos")
    
    novo_ticker = st.text_input("Ticker do Ativo:", placeholder="Ex: GARE11").upper().strip()
    
    if st.button("➕ ADICIONAR ATIVO", use_container_width=True):
        if novo_ticker:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("CREATE TABLE IF NOT EXISTS ativos (ticker TEXT PRIMARY KEY, preco REAL DEFAULT 0, pvp REAL DEFAULT 0, yield_anual REAL DEFAULT 0, dividendo REAL DEFAULT 0, data_coleta TEXT)")
            conn.execute("INSERT OR IGNORE INTO ativos (ticker, preco, pvp, yield_anual, dividendo) VALUES (?,0,0,0,0)", (novo_ticker,))
            conn.commit()
            conn.close()
            st.success(f"Sucesso: {novo_ticker} adicionado.")
            st.toast(f"Ativo {novo_ticker} salvo no banco.", icon="✅")
            time.sleep(1)
            st.rerun()

    st.divider()

    if st.button("🚀 SINCRONIZAR MERCADO", type="primary", use_container_width=True):
        with st.status("Robo extraindo dados...") as status:
            try:
                subprocess.run([sys.executable, ROBO_SCRIPT], check=True)
                status.update(label="Sincronia concluída!", state="complete")
                st.rerun()
            except Exception as e:
                st.error(f"Erro no Robo: {e}")

    st.divider()

    if st.button("🗑️ LIMPAR BANCO DE DADOS", use_container_width=True):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            st.rerun()

# ==========================================
# LADO DIREITO: DASHBOARD ANALÍTICO
# ==========================================
df = carregar_dados()

if not df.empty:
    st.title("📈 Monitoramento de Ativos")
    
    ativo_selecionado = st.selectbox("Selecione o ativo da sua lista:", df['ticker'].tolist())
    dados = df[df['ticker'] == ativo_selecionado].iloc[0]

    # --- ABA DE OPORTUNIDADE/STATUS PERMANENTE ---
    pvp = dados['pvp']
    if pvp == 0:
        st.markdown(f"<div class='status-box status-aguardando'>🕒 <b>Aguardando Sincronia:</b> Os dados para {ativo_selecionado} ainda não foram coletados. Clique em Sincronizar.</div>", unsafe_allow_html=True)
    elif pvp <= 0.98:
        st.markdown(f"<div class='status-box status-oportunidade'>💡 <b>Oportunidade:</b> {ativo_selecionado} está descontado (P/VP {pvp:.2f}). Ativo abaixo do valor patrimonial.</div>", unsafe_allow_html=True)
    elif pvp >= 1.05:
        st.markdown(f"<div class='status-box status-caro'>⚠️ <b>Atenção:</b> {ativo_selecionado} está com ágio elevado (P/VP {pvp:.2f}). Avalie o risco de entrada.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='status-box status-neutro'>⚖️ <b>Preço Equilibrado:</b> {ativo_selecionado} está sendo negociado próximo ao valor justo (P/VP {pvp:.2f}).</div>", unsafe_allow_html=True)

    # DADOS LIDOS PELO ROBÔ
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cotação Atual", f"R$ {dados['preco']:.2f}")
    col2.metric("P/VP Atual", f"{dados['pvp']:.2f}")
    col3.metric("Yield (12m)", f"{dados['yield_anual']:.2f}%")
    col4.metric("Últ. Provento", f"R$ {dados['dividendo']:.3f}")

    st.divider()

    # SIMULADOR DE CARTEIRA
    st.subheader("🧮 Simulador de Rendimento")
    c_sim1, c_sim2, c_sim3 = st.columns([1, 1.5, 1.5])
    
    with c_sim1:
        n_cotas = st.number_input("Cotas para Simular:", min_value=1, value=100, step=10)
    
    with c_sim2:
        custo_total = n_cotas * dados['preco']
        st.metric("Total a Investir", f"R$ {custo_total:,.2f}")
        
    with c_sim3:
        renda_total = n_cotas * dados['dividendo']
        st.metric("Renda Mensal Estimada", f"R$ {renda_total:,.2f}")

    st.divider()

    # GRÁFICO HORIZONTAL
    st.subheader("📊 Ranking de Dividendos por Cota")
    df_chart = df[df['dividendo'] > 0].sort_values('dividendo')
    
    if not df_chart.empty:
        fig = px.bar(
            df_chart, 
            x='dividendo', 
            y='ticker', 
            orientation='h',
            text_auto='.3f',
            color='dividendo',
            color_continuous_scale='Blues',
            template="plotly_dark",
            height=400
        )
        fig.update_layout(xaxis_title="Dividendo (R$)", yaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("O banco de dados está vazio. Utilize a barra lateral para adicionar ativos.")