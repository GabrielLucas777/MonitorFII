<<<<<<< HEAD
# 📊 monitorFII

> Ecossistema de monitoramento de Fundos de Investimento Imobiliário (FIIs) com coleta automatizada via RPA, armazenamento em banco de dados local e dashboard interativo para análise e recomendação de compra.

---

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)
=======
<div align="center">

# 🛡️ Sentinel Analytics
### *Inteligência de mercado para FIIs e Fiagros — sem planilhas, sem esforço manual.*

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Async-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Persistence-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visualização-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-MonitorFII-181717?style=flat-square&logo=github&logoColor=white)

<br/>

> **Sentinel** é uma plataforma de inteligência patrimonial que automatiza completamente o monitoramento de Fundos de Investimento Imobiliário (FIIs) e Fiagros — eliminando planilhas manuais e consolidando dados de mercado em tempo real em um único painel interativo.

</div>

---

## 📌 Sumário

- [Visão Geral](#-visão-geral)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Destaques Técnicos](#-destaques-técnicos)
- [Interface & UX](#-interface--ux)
- [Screenshots](#-screenshots)
- [Instalação & Execução](#-instalação--execução)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Roadmap](#-roadmap)

---

## 🧭 Visão Geral

O mercado de FIIs e Fiagros exige acompanhamento contínuo de dezenas de variáveis — P/VP, dividend yield, liquidez, setor, patrimônio líquido — em fontes dispersas e frequentemente desatualizadas. A solução convencional (planilhas manuais) é lenta, propensa a erros e não escala.

**Sentinel resolve isso com automação de ponta a ponta:**

- 🤖 **Coleta autônoma** via Web Scraping assíncrono com Playwright
- 🗄️ **Persistência estruturada** em banco SQLite com migração automática de schema
- 📊 **Dashboard interativo** construído em Streamlit + Plotly
- 🎯 **Simulador de aportes** para modelagem de renda passiva em tempo real
- 🚨 **Sistema de alertas** baseado em indicadores fundamentalistas (P/VP)

Nenhuma planilha. Nenhuma atualização manual. Apenas dados, visualizados com precisão.

---

## 🏗️ Arquitetura do Sistema

O projeto é desenhado com **separação explícita de responsabilidades**, garantindo que o motor de dados e a interface de usuário sejam completamente independentes e testáveis.

```
┌─────────────────────────────────────────────────────────┐
│                     SENTINEL ANALYTICS                  │
│                                                         │
│  ┌──────────────────────┐    ┌────────────────────────┐ │
│  │   2_robo.py          │    │   3_dashboard.py       │ │
│  │   [Motor Assíncrono] │    │   [Interface Streamlit]│ │
│  │                      │    │                        │ │
│  │  • Playwright async  │    │  • Plotly charts       │ │
│  │  • JS DOM injection  │    │  • Simulador dinâmico  │ │
│  │  • Rate limiting     │    │  • Alertas P/VP        │ │
│  │  • Error handling    │    │  • Filtros interativos │ │
│  └──────────┬───────────┘    └──────────┬─────────────┘ │
│             │                           │               │
│             ▼                           ▼               │
│        ┌────────────────────────────────────┐           │
│        │         fiis.db  (SQLite)          │           │
│        │   • Auto-migração de colunas       │           │
│        │   • Histórico de preços            │           │
│        │   • Snapshots de indicadores       │           │
│        └────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

| Módulo | Responsabilidade | Tecnologia-chave |
|---|---|---|
| `2_robo.py` | Coleta, parsing e persistência de dados | Playwright, asyncio, SQLite |
| `3_dashboard.py` | Visualização, simulação e alertas | Streamlit, Plotly, Pandas |
| `fiis.db` | Armazenamento persistente com schema evolutivo | SQLite + migração automática |

---

## ⚙️ Destaques Técnicos

### 🎯 Sniper Scraping — Extração Cirúrgica via Injeção de JS

O motor de scraping não depende de seletores CSS frágeis. Em vez disso, **injeta JavaScript diretamente no DOM** para acessar o estado interno da aplicação alvo — contornando proteções anti-bot baseadas em comportamento de browser, renderização lazy e ofuscação de elementos.

```python
# Exemplo: extração via execução de JS no contexto da página
raw_value = await page.evaluate("""
    () => document.querySelector('[data-testid="pvp"]')
          ?.textContent?.trim()
""")
```

Essa abordagem garante dados **limpos, precisos e resistentes a mudanças de layout** na interface do site-fonte.

---

### 📐 Simulador Dinâmico de Aportes

A interface de simulação permite que o investidor modele cenários de aporte com **precisão de 3 casas decimais**, calculando em tempo real:

- Quantidade de cotas adquiridas por valor aportado
- Renda mensal estimada (dividendos projetados)
- Yield on Cost personalizado por preço de entrada
- Comparação entre múltiplos FIIs no mesmo cenário

Toda a lógica de cálculo é reativa: qualquer alteração nos sliders ou campos recalcula instantaneamente o resultado — sem recarregamento de página.

---

### 🗄️ Data Persistence com Migração Automática de Schema

O banco SQLite é gerenciado com uma lógica própria de **migração incremental de colunas** — dispensando ferramentas externas como Alembic. Ao inicializar, o sistema detecta automaticamente colunas ausentes e as adiciona sem perda de dados históricos:

```python
def migrate_columns(conn: sqlite3.Connection, expected_cols: dict):
    existing = {row[1] for row in conn.execute("PRAGMA table_info(fiis)")}
    for col, dtype in expected_cols.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE fiis ADD COLUMN {col} {dtype}")
    conn.commit()
```

Isso garante **integridade total dos dados** mesmo quando novos indicadores são adicionados em versões futuras do robô.

---

## 🎨 Interface & UX

### 🚨 Sistema de Alertas por P/VP

O dashboard implementa um **sistema de sinalização visual minimalista** baseado no indicador P/VP (Preço sobre Valor Patrimonial) — um dos principais termômetros de valuation em FIIs:

| Condição | Sinal | Interpretação |
|---|---|---|
| P/VP ≤ 0.95 | 🟢 **Oportunidade** | Fundo sendo negociado com desconto sobre o patrimônio |
| 0.95 < P/VP ≤ 1.05 | 🟡 **Neutro** | Preço próximo ao valor justo |
| P/VP > 1.05 | 🔴 **Ágio** | Fundo sendo negociado acima do valor patrimonial |

Esses alertas são exibidos diretamente nas cards de cada FII, guiando a tomada de decisão **sem sobrecarregar o investidor com informação desnecessária**.

---

## 📸 Screenshots

### Dashboard Principal

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│          [ SCREENSHOT — Visão Geral do Dashboard ]         │
│                                                             │
│   Substitua este bloco pela imagem: docs/screenshot_01.png │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Simulador de Aportes

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│         [ SCREENSHOT — Simulador Dinâmico de Renda ]       │
│                                                             │
│   Substitua este bloco pela imagem: docs/screenshot_02.png │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Painel de Alertas P/VP

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│        [ SCREENSHOT — Sistema de Alertas P/VP ]            │
│                                                             │
│   Substitua este bloco pela imagem: docs/screenshot_03.png │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> 💡 Para adicionar screenshots: salve as imagens em `/docs/` e substitua os blocos acima por `![Alt](docs/nome_da_imagem.png)`.

---

## 🚀 Instalação & Execução

### Pré-requisitos

- Python **3.11+**
- pip atualizado (`pip install --upgrade pip`)

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/MonitorFII.git
cd MonitorFII
```

### 2. (Opcional) Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
```

### 3. Instalar dependências Python

```bash
pip install streamlit playwright plotly
```

### 4. Instalar os browsers do Playwright

```bash
playwright install
```

> Este comando baixa os binários do Chromium, Firefox e WebKit necessários para o scraping headless.

### 5. Executar o robô (coleta de dados)

```bash
python 2_robo.py
```

O robô irá coletar os dados e popular o banco `fiis.db` automaticamente.

### 6. Iniciar o dashboard

```bash
streamlit run 3_dashboard.py
```

Acesse em: **http://localhost:8501**
>>>>>>> 66aaed6 (Versão 2.0 com integração a fastAPI e otimização no dashboard)

---

## 📁 Estrutura do Projeto

```
<<<<<<< HEAD
monitorFII/
├── 2_robo.py           # RPA de coleta e persistência de dados
├── 3_dashboard.py      # Dashboard interativo via Streamlit
├── requirements.txt    # Dependências do projeto
├── fii.db              # Banco de dados SQLite (gerado automaticamente)
=======
MonitorFII/
│
├── 2_robo.py              # Motor assíncrono de scraping (Playwright)
├── 3_dashboard.py         # Interface interativa (Streamlit + Plotly)
├── fiis.db                # Banco de dados SQLite (gerado na primeira execução)
│
├── docs/                  # Assets de documentação
│   ├── screenshot_01.png
│   ├── screenshot_02.png
│   └── screenshot_03.png
│
>>>>>>> 66aaed6 (Versão 2.0 com integração a fastAPI e otimização no dashboard)
└── README.md
```

---

<<<<<<< HEAD
## ✨ Funcionalidades

### 🤖 RPA de Coleta — `2_robo.py`
- Realiza a coleta automatizada de dados de FIIs a partir de fontes externas.
- Persiste os registros no banco de dados SQLite local (`fii.db`).
- Aplica sanitização de dados antes da inserção, utilizando as funções `UPPER(TRIM())` diretamente nas queries SQL, garantindo consistência e eliminando ruídos como espaços extras e variações de caixa nos campos textuais.

### 📈 Dashboard Interativo — `3_dashboard.py`
- Interface construída com **Streamlit** para visualização e análise dos FIIs monitorados.
- Gráficos de dispersão renderizados com `px.scatter` (Plotly Express), estratégia deliberada para **evitar bugs de escala** presentes em gráficos de linha com séries temporais esparsas.
- **Tratamento de erro robusto:** caso o banco possua menos de 2 registros para um determinado FII, o dashboard exibe uma mensagem informativa ao usuário em vez de lançar uma exceção, garantindo estabilidade da aplicação.

### 💡 Lógica de Recomendação de Compra
- O sistema avalia automaticamente cada FII monitorado com base no seguinte critério:

```
Recomendação de Compra → Preço Atual < Média Histórica de Preços
```

- FIIs que atendem ao critério são destacados no dashboard como oportunidades de aporte, auxiliando na tomada de decisão fundamentada em dados históricos.

---

## ⚙️ Instalação e Configuração

### Pré-requisitos

- Python 3.10 ou superior
- `pip` atualizado

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/monitorFII.git
cd monitorFII
```

### 2. Crie e ative o ambiente virtual

```bash
# Criação do venv
python -m venv venv

# Ativação — Linux/macOS
source venv/bin/activate

# Ativação — Windows
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## ▶️ Execução

### Rodar o Robô de Coleta

Execute o RPA para coletar e persistir os dados mais recentes dos FIIs no banco local:

```bash
python 2_robo.py
```

> Recomenda-se agendar a execução periódica deste script (ex.: via `cron` no Linux ou Agendador de Tarefas no Windows) para manter os dados atualizados.

### Iniciar o Dashboard

```bash
streamlit run 3_dashboard.py
```

O Streamlit abrirá automaticamente o dashboard no navegador padrão em `http://localhost:8501`.

---

## 🗄️ Banco de Dados

O projeto utiliza **SQLite** como solução de persistência local, sem necessidade de infraestrutura externa. O arquivo `fii.db` é criado automaticamente na primeira execução do robô.

A sanitização aplicada via `UPPER(TRIM())` nas operações de escrita assegura integridade referencial e evita duplicatas causadas por inconsistências de formatação nos dados brutos coletados.

---

## 📦 Dependências

As principais bibliotecas utilizadas estão listadas em `requirements.txt`:

| Biblioteca   | Finalidade                              |
|--------------|-----------------------------------------|
| `streamlit`  | Interface web do dashboard              |
| `plotly`     | Geração de gráficos interativos         |
| `pandas`     | Manipulação e análise de dados          |
| `requests`   | Requisições HTTP no RPA de coleta       |
| `sqlite3`    | Nativo do Python — persistência local   |

---

## 🔒 Boas Práticas Implementadas

- **Sanitização de dados** na camada de persistência com `UPPER(TRIM())`.
- **Resiliência no dashboard** com tratamento explícito de casos com volume insuficiente de dados (< 2 registros).
- **Escolha técnica de `px.scatter`** sobre `px.line` para evitar comportamentos inesperados de escala em séries com baixa densidade de pontos.
- **Isolamento de dependências** via `venv`, evitando conflitos com o ambiente Python do sistema.

---

## 👨‍💻 Desenvolvedor

Desenvolvido por **Gabriel Santos**.

---

*monitorFII — Inteligência de dados a serviço do investidor em FIIs.*
=======
## 🗺️ Roadmap

- [ ] Suporte a alertas via Telegram/WhatsApp
- [ ] Comparativo histórico de DY por período (12M, 24M)
- [ ] Exportação de carteira em PDF com análise fundamentalista
- [ ] Agendamento automático do robô via cron/task scheduler
- [ ] Suporte a ETFs de renda fixa (IMAB11, IRFM11)

---

<div align="center">

Desenvolvido com foco em **automação, precisão e experiência do investidor**.

*Sentinel Analytics — Dados que trabalham por você.*

</div>
>>>>>>> 66aaed6 (Versão 2.0 com integração a fastAPI e otimização no dashboard)
