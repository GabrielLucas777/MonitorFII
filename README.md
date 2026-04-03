# 📊 monitorFII

> Ecossistema de monitoramento de Fundos de Investimento Imobiliário (FIIs) com coleta automatizada via RPA, armazenamento em banco de dados local e dashboard interativo para análise e recomendação de compra.

---

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)

---

## 📁 Estrutura do Projeto

```
monitorFII/
├── 2_robo.py           # RPA de coleta e persistência de dados
├── 3_dashboard.py      # Dashboard interativo via Streamlit
├── requirements.txt    # Dependências do projeto
├── fii.db              # Banco de dados SQLite (gerado automaticamente)
└── README.md
```

---

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
