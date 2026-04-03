# 🛰️ MonitorFII - Sentinel Intelligence

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

Sistema inteligente de monitoramento e análise de Fundos de Investimento Imobiliário (FIIs), projetado para automatizar a coleta de dados e fornecer insights de compra baseados em médias históricas de mercado.
## 🚀 Funcionalidades Principais

- **Automação de Coleta (RPA):** Motor de busca que percorre a carteira de ativos e persiste preços reais com timestamp no banco de dados.
- **Sanitização de Dados (Clean Code):** Tratamento de strings (`Upper/Trim`) na entrada do banco para garantir integridade e evitar duplicidade de ativos.
- **Lógica de Recomendação:** Algoritmo que compara o preço atual com a média histórica para identificar oportunidades de compra (Preço < Média).
- **Interface Resiliente:** Dashboard dinâmico com tratamento de erros para dados insuficientes e falhas de bibliotecas.

## 🛠️ Arquitetura do Projeto

O ecossistema é modularizado em três pilares fundamentais:

1.  **`2_robo.py`**: Responsável pelo scraping (coleta) e persistência de dados.
2.  **`3_dashboard.py`**: Interface de usuário (UI) focada em Data Visualization.
3.  **`investimentos.db`**: Banco de dados relacional SQLite para histórico de longo prazo.

## 📋 Como Instalar e Rodar

### 1. Configurar Ambiente Virtual (Recomendado)
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

### 2. Instalar Dependências

pip install -r requirements.txt

3. Execução
Para popular o banco com dados de teste ou reais:

python 2_robo.py

## 🧠 Decisões Técnicas de Engenharia

- **Gráfico de Pontos (Scatter):** Implementado para garantir melhor visualização em ativos com baixa variação e evitar bugs de escala de gráficos de barras convencionais.
- **Tratamento de Exceção:** Bloqueio de renderização quando o banco possui menos de 2 registros, fornecendo um diagnóstico claro ao usuário em vez de um erro genérico.
- **Integridade de Busca:** Consultas SQL utilizando `UPPER(TRIM(ticker))` para neutralizar erros de digitação humana ou "sujeira" nos dados capturados via automação.

---

### 👨‍💻 Desenvolvedor
**Gabriel Lucas**
*Foco em Automação, Python e Engenharia de Software.*
