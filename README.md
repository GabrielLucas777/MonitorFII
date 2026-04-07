<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Playwright-1.40+-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright">
  <img src="https://img.shields.io/badge/Pydantic-2.x-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
</p>

---

## Visao Geral

O MonitorFII e um sistema de Business Intelligence para analise de Fundos Imobiliarios (FIIs) com extracao automatizada de dados. A plataforma coleta indicadores fundamentalistas diretamente de fontes de mercado, persiste em banco de dados local e apresenta um dashboard interativo para tomada de decisao de investimento.

Nenhuma planilha. Nenhuma atualizacao manual. Dados sincronizados sob demanda.

---

## Estrutura do Projeto

```
monitor_de_ativos/
├── app.py                  # Dashboard Streamlit -- interface principal
├── run_scraper.py          # Wrapper de scraping via subprocesso
├── fii.db                  # Banco de dados SQLite (gerado automaticamente)
│
├── src/
│   ├── __main__.py         # CLI para operacoes em linha de comando
│   ├── config.py           # Configuracoes, URLs e script JS de extracao
│   ├── models.py           # Schemas Pydantic v2 para validacao de dados
│   ├── database.py         # CRUD SQLite com auto-migracao de schema
│   └── scraper.py          # Motor de scraping assincrono com Playwright
```

A arquitetura foi desenhada com separacao explicita de responsabilidades:

| Camada | Modulo | Responsabilidade |
|---|---|---|
| Interface | `app.py` | Dashboard, indicadores e calculadora |
| Coleta | `scraper.py` | Extracao via Playwright com scripts de injecao JS |
| Validacao | `models.py` | Schemas Pydantic v2 -- parsing de moeda BR e regras de negocio |
| Persistencia | `database.py` | CRUD SQLite com migracao automatica de colunas |
| Orquestracao | `run_scraper.py` | Wrapper chamado pelo dashboard e pela CLI |

A validacao via **Pydantic v2** e o componente central de integridade dos dados. O parser `_parse_br()` converte formatos brasileiros como `"R$ 1.098,56"` e `"12,23%"` em `Decimal`, enquanto os `@model_validator` aplicam regras de negocio -- como deteccao de escala para P/VP -- antes que qualquer dado alcance o banco. Dados que nao passam pela validacao sao rejeitados silenciosamente, impedindo corrupcao do banco.

---

## Instalacao

### 1. Clonar o repositorio

```bash
git clone https://github.com/GabrielLucas777/MonitorFII.git
cd MonitorFII
```

### 2. Criar e ativar ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Executar o dashboard

```bash
streamlit run app.py
```

O dashboard abre automaticamente em **http://localhost:8501**.

### 5. Sincronizar dados

Dentro do dashboard, utilize a barra lateral para:

- **Adicionar ativo**: informe o ticker (ex: `MXRF11`) e o sistema coleta os dados automaticamente.
- **Sincronizar todos**: atualiza os indicadores de todos os ativos cadastrados.
- **Sincronizar individual**: na aba "Detalhe", atualize um ativo especifico.

### CLI alternativa

```bash
python -m src add MXRF11      # Adicionar e sincronizar
python -m src sync             # Sincronizar todos
python -m src sync-one MXRF11  # Sincronizar um ativo
python -m src list             # Listar ativos no banco
python -m src remove MXRF11    # Remover ativo
```

---

## Recursos Principais

### Cards de Ativos com Formatacao Condicional

Grade em tres colunas com status visual baseado no indicador P/VP:

| Condicao | Sinal | Interpretacao |
|---|---|---|
| P/VP <= 0.98 | Oportunidade | Fundo negociado abaixo do valor patrimonial |
| 0.98 < P/VP < 1.05 | Neutro | Preco proximo ao valor justo |
| P/VP >= 1.05 | Caro | Fundo com premio elevado sobre o patrimonio |

Os cards exibem cotacao, P/VP, dividend yield e ultimo dividendo em layout responsivo.

### Calculadora de Dividendos

Projecao de renda passiva baseada no numero de cotas. O calculo atualiza automaticamente ao alterar a quantidade, com metas configuraveis de renda mensal (R$ 500 a R$ 5.000/mes) e indicadores de progresso visual.

### Dashboard com KPIs e Filtragem

Indicadores de resumo no topo (total de ativos, sincronizados, DY medio, P/VP medio). Filtro por ticker e ordenacao por indicador. Aba de detalhes individuais com banner de recomendacao e acoes de sincronizacao/remocao.

---

Desenvolvido por **Gabriel Santos**.

*MonitorFII -- Inteligencia de dados a servico do investidor em FIIs.*
