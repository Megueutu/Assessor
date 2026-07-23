from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


def _normalize_currency(value: str) -> str:
    currency = value.strip().upper()
    if len(currency) != 3 or not currency.isalpha():
        raise ValueError("A moeda deve usar um código ISO de três letras, como USD ou EUR.")
    return currency


class ExchangeRateArgs(BaseModel):
    currency: str = Field(description="Código ISO da moeda, como USD, EUR ou GBP.")
    reference_date: date | None = Field(
        default=None,
        description="Data de referência no formato YYYY-MM-DD. Quando omitida, usa a última PTAX disponível.",
    )

    _validate_currency = field_validator("currency")(_normalize_currency)


class ExchangeHistoryArgs(BaseModel):
    currency: str = Field(description="Código ISO da moeda, como USD, EUR ou GBP.")
    start_date: date = Field(description="Data inicial inclusiva no formato YYYY-MM-DD.")
    end_date: date = Field(description="Data final inclusiva no formato YYYY-MM-DD.")

    _validate_currency = field_validator("currency")(_normalize_currency)

    @model_validator(mode="after")
    def validate_period(self):
        if self.end_date < self.start_date:
            raise ValueError("A data final deve ser igual ou posterior à data inicial.")
        if (self.end_date - self.start_date).days >= 366:
            raise ValueError("O período máximo para consulta é de 366 dias.")
        return self


class ExchangeVariationArgs(ExchangeHistoryArgs):
    pass


class CurrencyConversionArgs(BaseModel):
    amount: Decimal = Field(gt=0, description="Valor positivo que será convertido.")
    source_currency: str = Field(description="Código ISO da moeda de origem.")
    target_currency: str = Field(description="Código ISO da moeda de destino.")
    reference_date: date | None = Field(
        default=None,
        description="Data de referência no formato YYYY-MM-DD. Quando omitida, usa a última PTAX disponível.",
    )

    _validate_source_currency = field_validator("source_currency")(_normalize_currency)
    _validate_target_currency = field_validator("target_currency")(_normalize_currency)
