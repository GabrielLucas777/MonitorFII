from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "fii.db"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

CATEGORIAS = ["fundos-imobiliarios", "fiagros"]

URLS_STATUS = {
    "fundos-imobiliarios": "https://statusinvest.com.br/fundos-imobiliarios/{ticker}",
    "fiagros": "https://statusinvest.com.br/fiagros/{ticker}",
}

NAV_TOUT = 60_000        # navegacao ms
NAVIGATION_TIMEOUT = NAV_TOUT
WAIT_AFTER_LOAD = 5
DELAY_MIN = 5.0
DELAY_MAX = 7.0
MIN_DELAY_BETWEEN_REQUESTS = DELAY_MIN
MAX_DELAY_BETWEEN_REQUESTS = DELAY_MAX

SCRAPE_SCRIPT = """
() => {
    const buscarPorTexto = (label) => {
        const elementos = document.querySelectorAll('.item, .info, .sub-value');
        for (let el of elementos) {
            if ((el.innerText || "").toUpperCase().includes(label.toUpperCase())) {
                const valorEl = el.querySelector('strong, .value');
                return valorEl ? valorEl.innerText : null;
            }
        }
        return null;
    };
    return {
        preco: document.querySelector('div[title="Valor atual do ativo"] strong')?.innerText || null,
        pvp: buscarPorTexto('P/VP'),
        yld: buscarPorTexto('Dividend Yield'),
        div: document.querySelector('#dy-info strong')?.innerText || null
    };
}
"""
