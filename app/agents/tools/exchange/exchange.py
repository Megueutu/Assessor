from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from langchain.tools import tool

from app.agents.tools.exchange.args import (
    CurrencyConversionArgs,
    ExchangeHistoryArgs,
    ExchangeRateArgs,
    ExchangeVariationArgs,
)
from app.agents.tools.exchange.client import (
    PTAX_SOURCE_URL,
    PtaxClient,
    PtaxClientError,
    quote_date,
)
from app.agents.tools.response import ToolResponse


_CLIENT = PtaxClient()
_MONEY_QUANTUM = Decimal("0.01")
_RATE_QUANTUM = Decimal("0.000001")
_PERCENT_QUANTUM = Decimal("0.01")


def _source() -> dict:
    return {
        "name": "Banco Central do Brasil - PTAX",
        "url": PTAX_SOURCE_URL,
        "frequency": "daily",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


def _serialize_rate(rate: dict) -> dict:
    return {
        "currency": rate["currency"],
        "buy": str(rate["buy"]),
        "sell": str(rate["sell"]),
        "quoted_at": rate["quoted_at"],
        "bulletin": rate["bulletin"],
    }


def _find_rate(currency: str, reference_date: date | None) -> dict | None:
    end_date = reference_date or date.today()
    start_date = end_date - timedelta(days=10)
    rates = _CLIENT.closing_rates(currency, start_date, end_date)
    return rates[-1] if rates else None


def _missing_rate(currency: str) -> dict:
    return ToolResponse.error(
        message=f"Não há cotação PTAX disponível para {currency} na data solicitada.",
        source=_source(),
    )


@tool("list_supported_currencies")
def list_supported_currencies() -> dict:
    """Lista as moedas disponíveis no serviço oficial PTAX do Banco Central."""
    try:
        currencies = _CLIENT.list_currencies()
        return ToolResponse.ok(currencies=currencies, total=len(currencies), source=_source())
    except PtaxClientError:
        return ToolResponse.error(
            message="Não foi possível consultar as moedas disponíveis no Banco Central.",
            source=_source(),
        )


@tool("get_exchange_rate", args_schema=ExchangeRateArgs)
def get_exchange_rate(currency: str, reference_date: date | None = None) -> dict:
    """Consulta a PTAX de fechamento mais recente até a data informada."""
    if currency == "BRL":
        return ToolResponse.ok(
            rate={
                "currency": "BRL",
                "buy": "1",
                "sell": "1",
                "quoted_at": (reference_date or date.today()).isoformat(),
                "bulletin": "Moeda base",
            },
            source=_source(),
        )

    try:
        rate = _find_rate(currency, reference_date)
        if rate is None:
            return _missing_rate(currency)
        return ToolResponse.ok(rate=_serialize_rate(rate), source=_source())
    except PtaxClientError:
        return ToolResponse.error(
            message="Não foi possível consultar a cotação no Banco Central.",
            source=_source(),
        )


@tool("get_exchange_history", args_schema=ExchangeHistoryArgs)
def get_exchange_history(currency: str, start_date: date, end_date: date) -> dict:
    """Consulta as cotações PTAX de fechamento em um período de até 366 dias."""
    if currency == "BRL":
        return ToolResponse.error(
            message="BRL é a moeda base da PTAX e não possui série própria.",
            source=_source(),
        )

    try:
        rates = _CLIENT.closing_rates(currency, start_date, end_date)
        if not rates:
            return _missing_rate(currency)
        return ToolResponse.ok(
            currency=currency,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            rates=[_serialize_rate(rate) for rate in rates],
            total=len(rates),
            source=_source(),
        )
    except PtaxClientError:
        return ToolResponse.error(
            message="Não foi possível consultar o histórico no Banco Central.",
            source=_source(),
        )


@tool("calculate_exchange_variation", args_schema=ExchangeVariationArgs)
def calculate_exchange_variation(currency: str, start_date: date, end_date: date) -> dict:
    """Calcula a variação da cotação PTAX de venda entre o primeiro e o último fechamento."""
    if currency == "BRL":
        return ToolResponse.error(
            message="BRL é a moeda base da PTAX e não possui variação própria.",
            source=_source(),
        )

    try:
        rates = _CLIENT.closing_rates(currency, start_date, end_date)
        if not rates:
            return _missing_rate(currency)

        first, last = rates[0], rates[-1]
        absolute = last["sell"] - first["sell"]
        percentage = (absolute / first["sell"]) * Decimal("100")
        return ToolResponse.ok(
            currency=currency,
            basis="PTAX de venda",
            first_rate=_serialize_rate(first),
            last_rate=_serialize_rate(last),
            absolute_variation=str(absolute.quantize(_RATE_QUANTUM, rounding=ROUND_HALF_UP)),
            percentage_variation=str(
                percentage.quantize(_PERCENT_QUANTUM, rounding=ROUND_HALF_UP)
            ),
            source=_source(),
        )
    except PtaxClientError:
        return ToolResponse.error(
            message="Não foi possível calcular a variação cambial.",
            source=_source(),
        )


@tool("convert_currency", args_schema=CurrencyConversionArgs)
def convert_currency(
    amount: Decimal,
    source_currency: str,
    target_currency: str,
    reference_date: date | None = None,
) -> dict:
    """Converte moedas com as cotações PTAX de compra e venda, sem spread ou tributos."""
    if source_currency == target_currency:
        return ToolResponse.ok(
            amount=str(amount),
            source_currency=source_currency,
            target_currency=target_currency,
            converted_amount=str(amount.quantize(_MONEY_QUANTUM, rounding=ROUND_HALF_UP)),
            calculation="Moedas de origem e destino são iguais.",
            source=_source(),
        )

    try:
        source_rate = None if source_currency == "BRL" else _find_rate(source_currency, reference_date)
        target_rate = None if target_currency == "BRL" else _find_rate(target_currency, reference_date)

        if source_currency != "BRL" and source_rate is None:
            return _missing_rate(source_currency)
        if target_currency != "BRL" and target_rate is None:
            return _missing_rate(target_currency)

        if source_rate and target_rate and quote_date(source_rate) != quote_date(target_rate):
            return ToolResponse.error(
                message="Não há cotações das duas moedas na mesma data de referência.",
                source=_source(),
            )

        value_in_brl = amount if source_rate is None else amount * source_rate["buy"]
        converted = value_in_brl if target_rate is None else value_in_brl / target_rate["sell"]
        quoted_at = (
            source_rate["quoted_at"]
            if source_rate
            else target_rate["quoted_at"] if target_rate else reference_date or date.today()
        )

        return ToolResponse.ok(
            amount=str(amount),
            source_currency=source_currency,
            target_currency=target_currency,
            converted_amount=str(converted.quantize(_MONEY_QUANTUM, rounding=ROUND_HALF_UP)),
            quoted_at=str(quoted_at),
            calculation=(
                "Moeda estrangeira de origem pela PTAX de compra; "
                "moeda estrangeira de destino pela PTAX de venda."
            ),
            excludes=["spread da instituição", "IOF", "tarifas"],
            source=_source(),
        )
    except PtaxClientError:
        return ToolResponse.error(
            message="Não foi possível converter as moedas com dados do Banco Central.",
            source=_source(),
        )
