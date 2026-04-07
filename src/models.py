"""Pydantic v2 schemas — validação e sanitizacao de dados FII."""

from __future__ import annotations

import re
from decimal import Decimal

from pydantic import BaseModel, field_validator, model_validator


# ────────────── Parser BR → Decimal ──────────────
_BR_STRIP = re.compile(r"[^\d,\-]")


def _parse_br(v: str | float | None) -> Decimal:
    """Converte 'R$ 1.234,56' / '98,5%' / '---' em Decimal seguro."""
    if v is None:
        return Decimal("0")
    s = str(v).replace("R$", "").replace("%", "").strip()
    if not s or s in ("-", "N/A", "---"):
        return Decimal("0")
    s = _BR_STRIP.sub("", s)
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


# ────────────── Schemas ──────────────
class AtivoInput(BaseModel):
    """Dados crus extraídos do HTML (strings BR)."""

    ticker: str
    preco: str | None = None
    pvp: str | None = None
    yld: str | None = None
    div: str | None = None

    @field_validator("ticker", mode="before")
    @classmethod
    def _upper(cls, v: str) -> str:
        return str(v).upper().strip()

    @field_validator("ticker")
    @classmethod
    def _ticker_fmt(cls, v: str) -> str:
        if not re.match(r"^[A-Z]{3,6}\d{2}$", v):
            raise ValueError(f"Ticker invalido: {v}")
        return v


class Ativo(BaseModel):
    """Dados validados e tipados — prontos para persistencia."""

    ticker: str
    preco: Decimal = Decimal("0")
    pvp: Decimal = Decimal("0")
    yield_anual: Decimal = Decimal("0")
    dividendo: Decimal = Decimal("0")

    @field_validator("ticker", mode="before")
    @classmethod
    def _upper(cls, v):
        return str(v).upper().strip()

    @field_validator("ticker")
    @classmethod
    def _ticker_fmt(cls, v: str) -> str:
        if not re.match(r"^[A-Z]{3,6}\d{2}$", v):
            raise ValueError(f"Ticker invalido: {v}")
        return v

    @model_validator(mode="before")
    @classmethod
    def _parse_values(cls, data: dict) -> dict:
        return {
            **data,
            "preco": _parse_br(data.get("preco")),
            "pvp": _parse_br(data.get("pvp")),
            "yield_anual": _parse_br(data.get("yield_anual")),
            "dividendo": _parse_br(data.get("dividendo")),
        }

    @model_validator(mode="after")
    def _business_rules(self) -> Ativo:
        if self.pvp < 0:
            raise ValueError("P/VP nao pode ser negativo")
        if self.yield_anual < 0:
            raise ValueError("Yield nao pode ser negativo")
        # Correcao de escala: se pvp > 50, veio em centesimos (ex: 101 → 1.01)
        if self.pvp > 50:
            object.__setattr__(self, "pvp", self.pvp / 100)
        return self

    def to_dict(self) -> dict[str, float]:
        return {
            "ticker": self.ticker,
            "preco": float(self.preco),
            "pvp": float(self.pvp),
            "yield_anual": float(self.yield_anual),
            "dividendo": float(self.dividendo),
        }
