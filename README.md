# 📊 monitorFII

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?style=for-the-badge&logo=sqlite)
![Plotly](https://img.shields.io/badge/Plotly-Visualização-3f4f75?style=for-the-badge&logo=plotly)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)

---

## 📌 Sobre o Projeto

O **monitorFII** é um ecossistema de monitoramento de Fundos Imobiliários (FIIs) desenvolvido em Python.  
O sistema realiza coleta automatizada de dados, tratamento e persistência em banco local, além de disponibilizar um dashboard interativo para análise e tomada de decisão.

---

## 🚀 Arquitetura do Projeto

O projeto é dividido em três camadas principais:

- **Coleta de Dados (RPA)** → `2_robo.py`
- **Persistência (Banco de Dados)** → SQLite
- **Visualização (Dashboard)** → `3_dashboard.py`

---

## ⚙️ Funcionalidades

### 🤖 Coleta Automatizada (RPA)
- Script `2_robo.py` responsável pela extração de dados de FIIs
- Execução automatizada para atualização contínua da base
- Estruturado para fácil expansão de fontes de dados

---

### 🧹 Tratamento e Padronização de Dados
- Sanitização aplicada diretamente no banco:
  ```sql
  UPPER(TRIM(campo))

  Garante:
Consistência textual
Eliminação de espaços inválidos
Padronização para queries confiáveis
📈 Lógica de Recomendação
Estratégia simples e eficiente:

Recomendação de compra quando:
Preço Atual < Média Histórica
Permite identificar oportunidades com base em comportamento histórico
📊 Dashboard Interativo
Construído com Streamlit
Visualizações com Plotly
🔹 Resiliência implementada:
Uso de px.scatter para evitar problemas de escala em gráficos
Tratamento de erro para cenários com poucos dados:
Evita quebra quando há menos de 2 registros no banco
Garante estabilidade da aplicação
🗄️ Banco de Dados
Banco local utilizando SQLite
Estrutura leve e eficiente para prototipagem e uso individual
Ideal para projetos de automação e análise local
🛠️ Tecnologias Utilizadas
Python
Streamlit
SQLite
Pandas
Plotly
⚡ Como Executar o Projeto
🔹 1. Criar ambiente virtual
python -m venv venv
🔹 2. Ativar ambiente virtual

Windows:

venv\Scripts\activate

Linux/Mac:

source venv/bin/activate
🔹 3. Instalar dependências
pip install -r requirements.txt
🔹 4. Executar o robô de coleta
python 2_robo.py
🔹 5. Rodar o dashboard
streamlit run 3_dashboard.py
📂 Estrutura do Projeto
monitorFII/
├── 2_robo.py          # RPA de coleta de dados
├── 3_dashboard.py     # Dashboard interativo
├── database.db        # Banco SQLite
├── requirements.txt
└── README.md
📌 Considerações Técnicas
Arquitetura modular facilita manutenção e expansão
Uso de SQLite reduz complexidade de infraestrutura
Pipeline simples e eficiente: Coleta → Tratamento → Visualização
Preparado para evolução futura (APIs, alertas, deploy)
👨‍💻 Autor

Gabriel Santos
