# 🛰️ MonitorFII - Sentinel Intelligence

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

Sistema inteligente de monitoramento e análise de Fundos de Investimento Imobiliário (FIIs), projetado para automatizar a coleta de dados e fornecer insights de compra baseados em médias históricas de mercado.

## 🚀 Funcionalidades Principais

- **Automação de Coleta (RPA):** Motor de busca que percorre a carteira de ativos e persiste preços reais com data e hora.
- **Sanitização de Dados (Clean Code):** Tratamento rigoroso de strings (`Upper/Trim`) na entrada do banco para garantir integridade referencial.
- **Lógica de Recomendação Financeira:** Algoritmo que compara o preço atual com a média histórica para identificar oportunidades de desconto.
- **Resiliência Visual:** Dashboard dinâmico com tratamento de erros e verificação de massa de dados mínima para plotagem de gráficos de dispersão (Scatter).

## 🛠️ Arquitetura do Projeto

O ecossistema é modularizado em três pilares:

1.  **`2_robo.py`**: Motor de scraping e persistência de dados.
2.  **`3_dashboard.py`**: Interface de usuário (UI) focada em Data Visualization.
3.  **`investimentos.db`**: Banco de dados relacional SQLite.

## 📋 Como Instalar e Rodar

### 1. Configurar Ambiente Virtual
```bash
python -m venv venv
# No Windows: venv\Scripts\activate
pip install -r requirements.txt
2. Execução
Para popular o banco com dados:

Bash
python 2_robo.py

Para visualizar o terminal de decisão:

Bash
streamlit run 3_dashboard.py

🧠 Decisões Técnicas de Engenharia
Gráfico de Pontos (Scatter): Implementado para garantir melhor visualização em ativos com baixa volatilidade e evitar bugs de escala.

Tratamento de Exceção: Bloqueio de renderização quando o banco possui dados insuficientes (menos de 2 registros), fornecendo diagnóstico claro ao usuário.

Integridade de String: Busca SQL utilizando UPPER(TRIM(ticker)) para neutralizar erros de input ou sujeira nos dados capturados.

👨‍💻 Desenvolvedor
Gabriel Lucas
