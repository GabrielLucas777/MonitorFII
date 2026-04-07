"""app.py — MonitorFII Dashboard Premium."""

from __future__ import annotations

import json
import subprocess as _sub
import sys

import pandas as pd
import streamlit as st
import requests

from src.database import init_db, upsert, add, get_all, get_one, delete, clear, summary
from src.config import DB_PATH

# Palette
ROXO = "#7D4CDB"
VERDE = "#10B981"
VERMELHO = "#EF4444"
AMBAR = "#F59E0B"
AZUL = "#3B82F6"
CINZA = "#6B7280"
CIANO = "#06B6D4"

_BG = "#0E1117"
_BG2 = "#161B22"
_TXT = "#FAFAFA"
_TXT2 = "#9CA3AF"
_BORDER = "rgba(255,255,255,0.08)"
_SHADOW = "rgba(0,0,0,0.15)"

st.set_page_config(
    page_title="MonitorFII",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────── API helpers ──────────────
API_URL = "http://127.0.0.1:8000"


def api_alive():
    try:
        return requests.get(f"{API_URL}/health", timeout=3).status_code == 200
    except Exception:
        return False


# ────────────── CSS ──────────────
st.html(
    """
<style>
  /* ── Custom components ── */
  .kpi { background: #161B22; border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 18px 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
  .kpi .label { font-size: 0.75rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.6px; }
  .kpi .value { font-size: 1.7rem; font-weight: 700; margin-top: 4px; }
  .kpi .accent { width: 40px; height: 4px; border-radius: 2px; margin-bottom: 8px; }

  .asset-card { background: #161B22; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.15); cursor: pointer; transition: border-color 0.2s, box-shadow 0.2s; }
  .asset-card:hover { border-color: #7D4CDB66; box-shadow: 0 4px 24px rgba(0,0,0,0.15); }

  .badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 16px; border-radius: 999px; font-weight: 700; font-size: 0.78rem; letter-spacing: 0.4px; text-transform: uppercase; }
  .badge-ok   { background: #10B98122; color: #10B981; border: 1px solid #10B98144; }
  .badge-warn { background: #EF444422; color: #EF4444; border: 1px solid #EF444444; }
  .badge-info { background: #3B82F622; color: #3B82F6; border: 1px solid #3B82F644; }

  .rec-box { border-left: 5px solid; padding: 16px 24px; border-radius: 0 10px 10px 0; margin-bottom: 22px; font-size: 1rem; }

  /* ── Sidebar premium ── */
  .sidebar-header { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.2px; color: #9CA3AF; margin-bottom: 4px; }
  .sidebar-logo { font-size: 1.15rem; font-weight: 800; color: #FAFAFA; margin-bottom: 20px; }
  .sidebar-logo span { color: #06B6D4; }
  .sidebar-section { margin-bottom: 6px; }
  .sidebar-section .sec-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.8px; color: #9CA3AF; margin-bottom: 8px; font-weight: 600; }
  .status-working { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 8px; margin-top: 10px; border: 1px solid rgba(125,76,219,0.3); background: rgba(125,76,219,0.08); font-size: 0.82rem; color: #7D4CDB; }
  .status-working .dot { width: 8px; height: 8px; border-radius: 50%; background: #7D4CDB; animation: pulse 1.2s ease-in-out infinite; }
  @keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
</style>
"""
)

# ────────────── Init ──────────────
init_db()

# ────────────── Helpers ──────────────
def kpi(label: str, value: str, delta: str = "", color: str = ROXO):
    delta_html = f'<div class="label" style="margin-top:4px">{delta}</div>' if delta else ""
    st.html(
        f'<div class="kpi">'
        f'<div class="accent" style="background:{color}"></div>'
        f'<div class="label">{label}</div>'
        f'<div class="value" style="color:{color}">{value}</div>'
        f'{delta_html}'
        f'</div>'
    )


def classify(pvp: float) -> str:
    if pvp <= 0:
        return "—"
    if pvp <= 0.98:
        return "COMPRAR"
    if pvp >= 1.05:
        return "EVITAR"
    return "NEUTRO"


def badge(kind: str) -> str:
    if kind == "COMPRAR":
        return f'<span class="badge badge-ok">✔ Oportunidade</span>'
    if kind == "EVITAR":
        return f'<span class="badge badge-warn">✖ Caro</span>'
    return f'<span class="badge badge-info">~ Neutro</span>'


def rec_banner(pvp: float, ticker: str) -> str:
    if pvp <= 0:
        return (
            f'<div class="rec-box" style="border-color:{CINZA};background:{CINZA}18;color:{_TXT2}">'
            f"Sem dados — sincronize <b>{ticker}</b>.</div>"
        )
    if pvp <= 0.98:
        return (
            f'<div class="rec-box" style="border-color:{VERDE};background:{VERDE}12;color:{VERDE}">'
            f"✔ <b>Oportunidade</b> — {ticker} P/VP {pvp:.2f}. "
            f"Abaixo do valor patrimonial, bom momento para entrada.</div>"
        )
    if pvp >= 1.05:
        return (
            f'<div class="rec-box" style="border-color:{VERMELHO};background:{VERMELHO}12;color:{VERMELHO}">'
            f"✖ <b>Caro</b> — {ticker} P/VP {pvp:.2f}. Premio elevado; avalie o risco.</div>"
        )
    return (
        f'<div class="rec-box" style="border-color:{AZUL};background:{AZUL}12;color:{AZUL}">'
        f"~ <b>Neutro</b> — {ticker} P/VP {pvp:.2f}. Preco proximo ao valor justo.</div>"
    )


def fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}"


@st.cache_data(ttl=5, show_spinner=False)
def _fetch_data():
    if api_alive():
        try:
            r = requests.get(f"{API_URL}/ativos", timeout=8)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    return get_all()


@st.cache_data(ttl=5, show_spinner=False)
def _fetch_summary():
    if api_alive():
        try:
            r = requests.get(f"{API_URL}/dashboard/resumo", timeout=8)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    return summary()


with st.sidebar:
    st.html('<div class="sidebar-logo">Monitor<span>FII</span></div>')
    st.html('<div class="sidebar-header">Intelligence v2</div>')

    st.divider()

    # ── Seção: Adicionar ──
    st.html('<div class="sidebar-section"><div class="sec-label">Adicionar Ativo</div></div>')
    novo = st.text_input("", placeholder="Ticker do ativo (ex: MXRF11)")
    if novo:
        novo = novo.upper().strip()
        if st.button("Adicionar e coletar", type="primary", use_container_width=True):
            if get_one(novo):
                st.warning(f"{novo} ja existe no banco.")
            else:
                add(novo)
                st.html('<div class="status-working"><div class="dot"></div> Robo de coleta em execucao...</div>')
                with st.spinner():
                    try:
                        r = _sub.run(
                            [sys.executable, "run_scraper.py", novo],
                            capture_output=True, text=True, timeout=120,
                            cwd=str(DB_PATH.parent),
                        )
                        out = json.loads(r.stdout.strip()) if r.stdout.strip() else {}
                    except Exception:
                        out = {"status": "err"}
                if out.get("status") == "ok":
                    st.success(f"{novo} sincronizado com sucesso.")
                else:
                    st.info(f"{novo} adicionado. Sincronize os dados depois.")
                _fetch_data.clear()
                _fetch_summary.clear()
                st.rerun()
    st.divider()

    # ── Seção: Sincronizar ──
    st.html('<div class="sidebar-section"><div class="sec-label">Sincronizacao</div></div>')
    if st.button("Sincronizar todos", use_container_width=True):
        tickers = [r["ticker"] for r in get_all()]
        if tickers:
            st.html('<div class="status-working"><div class="dot"></div> Robo coletando dados dos ativos...</div>')
            with st.spinner():
                try:
                    r = _sub.run(
                        [sys.executable, "run_scraper.py", "all"],
                        capture_output=True, text=True, timeout=600,
                        cwd=str(DB_PATH.parent),
                    )
                    out = json.loads(r.stdout.strip()) if r.stdout.strip() else {}
                except Exception:
                    out = {"status": "err"}
            if out.get("status") == "done":
                st.success(f"{out['count']}/{out['total']} ativos sincronizados.")
            else:
                st.error("Erro na sincronizacao.")
            _fetch_data.clear()
            _fetch_summary.clear()
            st.rerun()
        else:
            st.info("Nenhum ativo cadastrado.")
    st.divider()

    # ── Seção: Dados ──
    st.html('<div class="sidebar-section"><div class="sec-label">Dados</div></div>')
    if st.button("Limpar banco", use_container_width=True):
        _fetch_data.clear()
        _fetch_summary.clear()
        clear()
        st.rerun()

    st.divider()
    st.html('<div style="font-size:0.68rem;color:#6B7280;letter-spacing:0.4px;">Built with Python & Playwright</div>')


# ────────────── Loading ──────────────
with st.spinner("Carregando dados dos ativos..."):
    ativos = _fetch_data()
    resumo = _fetch_summary()

if not ativos:
    st.info("📭 Nenhum ativo cadastrado. Use a barra lateral.")
    st.stop()

df = pd.DataFrame(ativos)
for c in ["preco", "pvp", "yield_anual", "dividendo"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

df["status"] = df["pvp"].apply(lambda x: classify(x))

# ────────────── KPIs ──────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi("Ativos", str(resumo.get("total", len(df))), "", CIANO)
with c2:
    kpi("Sincronizados", str(resumo.get("synced", 0)),
        f"{resumo.get('pending', 0)} pendentes" if resumo.get("pending", 0) else "OK", VERDE)
with c3:
    kpi("DY Medio", f"{resumo.get('avg_dy', 0):.2f}%", "", VERDE)
with c4:
    kpi("P/VP Medio", f"{resumo.get('avg_pvp', 0):.2f}", "", AZUL)

st.divider()

# ────────────── Tabs ──────────────
tab_cards, tab_detalhe, tab_calc = st.tabs([
    "📋 Carteirinha",
    "🔍 Detalhe",
    "🧮 Calculadora",
])


# ═══════════ TAB 1: Carteirinha ═══════════
with tab_cards:
    st.subheader("Seus Ativos")

    # Select control for filtering / sorting
    f1, f2 = st.columns([1, 2])
    with f1:
        sort_by = st.selectbox("Ordenar por:", [
            "Ticker", "P/VP (menor primeiro)", "DY (maior primeiro)",
            "Dividendo (maior primeiro)"
        ])
    with f2:
        search = st.text_input("Buscar ticker:", placeholder="Buscar...")

    filtered = df[df["ticker"].str.contains(search.upper())] if search else df

    if sort_by.startswith("Ticker"):
        filtered = filtered.sort_values("ticker")
    elif sort_by.startswith("P/VP"):
        filtered = filtered[filtered["pvp"] > 0].sort_values("pvp")
    elif sort_by.startswith("DY"):
        filtered = filtered[filtered["yield_anual"] > 0].sort_values("yield_anual", ascending=False)
    else:
        filtered = filtered[filtered["dividendo"] > 0].sort_values("dividendo", ascending=False)

    # Cards grid
    cols = st.columns(3)
    for idx, (_, row) in enumerate(filtered.iterrows()):
        t = row["ticker"]
        p = float(row["preco"])
        v = float(row["pvp"])
        dy = float(row["yield_anual"])
        div = float(row["dividendo"])
        stat = classify(v)
        border = VERDE if stat == "COMPRAR" else VERMELHO if stat == "EVITAR" else AZUL if stat == "NEUTRO" else CINZA

        card = f"""
        <div class="asset-card" style="border-top: 3px solid {border};">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="font-size:1.2rem;font-weight:800;color:{_TXT};">{t}</span>
                {badge(stat)}
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
                <div>
                    <div style="font-size:0.68rem;color:{_TXT2};text-transform:uppercase;">Preco</div>
                    <div style="font-size:1rem;font-weight:700;color:{_TXT};">{fmt_brl(p)}</div>
                </div>
                <div>
                    <div style="font-size:0.68rem;color:{_TXT2};text-transform:uppercase;">P/VP</div>
                    <div style="font-size:1rem;font-weight:700;color:{border if v > 0 else _TXT2};">{'{:.2f}'.format(v) if v > 0 else '—'}</div>
                </div>
                <div>
                    <div style="font-size:0.68rem;color:{_TXT2};text-transform:uppercase;">DY 12m</div>
                    <div style="font-size:1rem;font-weight:700;color:{VERDE if dy > 0 else _TXT2};">{'{:.2f}%'.format(dy) if dy > 0 else '—'}</div>
                </div>
            </div>
            <div style="margin-top:8px;font-size:0.78rem;color:{_TXT2};">
                Ult. div: {fmt_brl(div)}
            </div>
        </div>
        """
        with cols[idx % 3]:
            st.html(card)

    if filtered.empty:
        st.info("Nenhum ativo encontrado.")


# ═══════════ TAB 2: Detalhe ═══════════
with tab_detalhe:
    st.subheader("Detalhe do Ativo")

    sel = st.selectbox("Ativo:", sorted(df["ticker"].tolist()), key="det_sel")
    row = df[df["ticker"] == sel].iloc[0]
    pvp_val = float(row.get("pvp", 0))
    status = classify(pvp_val)

    st.html(rec_banner(pvp_val, sel))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cotacao", fmt_brl(float(row["preco"])))
    m2.metric("P/VP", f"{row['pvp']:.2f}")
    m3.metric("Div. Yield (12m)", f"{row['yield_anual']:.2f}%")
    m4.metric("Ult. Dividendo", fmt_brl(float(row["dividendo"])))

    st.html(badge(status))

    st.divider()
    b_sync, b_del = st.columns(2)
    with b_sync:
        if st.button("🔄 Sincronizar este ativo", use_container_width=True):
            with st.spinner(f"Coletando {sel}..."):
                try:
                    r = _sub.run(
                        [sys.executable, "run_scraper.py", sel],
                        capture_output=True, text=True, timeout=120,
                        cwd=str(DB_PATH.parent),
                    )
                    out = json.loads(r.stdout.strip()) if r.stdout.strip() else {}
                except Exception:
                    out = {"status": "err"}
            if out.get("status") == "ok":
                st.success(f"{sel} atualizado!")
            else:
                st.warning(f"Falha ao coletar dados de {sel}.")
            _fetch_data.clear()
            _fetch_summary.clear()
            st.rerun()
    with b_del:
        if st.button("🗑 Remover", use_container_width=True):
            delete(sel)
            _fetch_data.clear()
            _fetch_summary.clear()
            st.rerun()


# ═══════════ TAB 3: Calculadora ═══════════
with tab_calc:
    st.subheader("🧮 Calculadora de Dividendos")
    st.caption("Altere o numero de cotas — a projecao atualiza automaticamente.")

    s_cols = st.columns([1, 1])
    with s_cols[0]:
        sim_ativo = st.selectbox("Ativo base:", sorted(df["ticker"].tolist()), key="sim_a")
    with s_cols[1]:
        n_cotas = st.number_input("Numero de Cotas:", min_value=1, value=100, step=10, key="sim_n")

    ds = df[df["ticker"] == sim_ativo].iloc[0]
    preco = float(ds["preco"])
    div = float(ds["dividendo"])

    invest = n_cotas * preco
    renda_m = round(n_cotas * div, 2)
    renda_a = round(renda_m * 12, 2)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Investimento Total", fmt_brl(invest))
    c2.metric("💵 Renda Mensal Est.", fmt_brl(renda_m))
    c3.metric("📅 Renda Anual Est.", fmt_brl(renda_a))

    st.divider()
    st.subheader("🎯 Metas de Renda Mensal")

    metas = [
        (500, "Renda Extra"),
        (1000, "Salario Minimo"),
        (3000, "Salario Medio"),
        (5000, "Renda Confortavel"),
    ]

    for valor, nome in metas:
        pct = min(renda_m / valor, 1.0) if valor > 0 else 0
        done = renda_m >= valor
        falt = max(0, int((valor - renda_m) / div)) if div > 0 and not done else 0

        st.html(
            f"<p style='margin-bottom:4px;'>"
            f"{'<b>' if done else ''}{'✅' if done else '⬜'} {nome} — R$ {valor:,}/mes"
            f"{'</b>' if done else ''}"
            f"<span style='margin-left:8px;font-size:0.78rem;opacity:0.6;'>"
            f"{' — concluido!' if done else f' — faltam ~{falt} cotas'}</span>"
            f"</p>"
        )
        st.progress(pct)
