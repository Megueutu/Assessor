import unittest
from io import BytesIO
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from pydantic import ValidationError

from app.agents.tools.exchange.args import ExchangeHistoryArgs
from app.agents.tools.exchange import exchange
from app.agents.tools.exchange import client as ptax
from app.agents.tools.exchange.client import PtaxClient, PtaxClientError


def rate(currency, buy, sell, quoted_at):
    return {
        "currency": currency,
        "buy": Decimal(buy),
        "sell": Decimal(sell),
        "quoted_at": quoted_at,
        "bulletin": "Fechamento",
    }


class FakePtaxClient:
    def __init__(self, rates_by_currency=None, currencies=None, error=None):
        self.rates_by_currency = rates_by_currency or {}
        self.currencies = currencies or []
        self.error = error
        self.calls = []

    def list_currencies(self):
        if self.error:
            raise self.error
        return self.currencies

    def closing_rates(self, currency, start_date, end_date):
        if self.error:
            raise self.error
        self.calls.append((currency, start_date, end_date))
        return self.rates_by_currency.get(currency, [])


class TestExchangeTools(unittest.TestCase):
    def test_should_normalize_currency_and_reject_period_over_limit(self):
        args = ExchangeHistoryArgs(
            currency=" usd ",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
        )

        self.assertEqual(args.currency, "USD")
        with self.assertRaises(ValidationError):
            ExchangeHistoryArgs(
                currency="USD",
                start_date=date(2025, 1, 1),
                end_date=date(2026, 2, 1),
            )

    def test_should_return_last_available_closing_rate(self):
        client = FakePtaxClient({
            "USD": [
                rate("USD", "5.00", "5.01", "2026-07-20 13:00:00"),
                rate("USD", "5.10", "5.11", "2026-07-21 13:00:00"),
            ]
        })

        with patch.object(exchange, "_CLIENT", client):
            result = exchange.get_exchange_rate.func(
                currency="USD",
                reference_date=date(2026, 7, 22),
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["rate"]["sell"], "5.11")
        self.assertEqual(client.calls[0][1], date(2026, 7, 12))

    def test_should_calculate_sell_rate_variation(self):
        client = FakePtaxClient({
            "USD": [
                rate("USD", "4.99", "5.00", "2026-07-20 13:00:00"),
                rate("USD", "5.49", "5.50", "2026-07-21 13:00:00"),
            ]
        })

        with patch.object(exchange, "_CLIENT", client):
            result = exchange.calculate_exchange_variation.func(
                currency="USD",
                start_date=date(2026, 7, 20),
                end_date=date(2026, 7, 21),
            )

        self.assertEqual(result["absolute_variation"], "0.500000")
        self.assertEqual(result["percentage_variation"], "10.00")
        self.assertEqual(result["basis"], "PTAX de venda")

    def test_should_convert_foreign_currencies_through_brl(self):
        client = FakePtaxClient({
            "USD": [rate("USD", "5.00", "5.10", "2026-07-21 13:00:00")],
            "EUR": [rate("EUR", "6.00", "6.25", "2026-07-21 13:00:00")],
        })

        with patch.object(exchange, "_CLIENT", client):
            result = exchange.convert_currency.func(
                amount=Decimal("100"),
                source_currency="USD",
                target_currency="EUR",
                reference_date=date(2026, 7, 21),
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["converted_amount"], "80.00")
        self.assertIn("IOF", result["excludes"])

    def test_should_reject_cross_conversion_with_different_quote_dates(self):
        client = FakePtaxClient({
            "USD": [rate("USD", "5.00", "5.10", "2026-07-20 13:00:00")],
            "EUR": [rate("EUR", "6.00", "6.10", "2026-07-21 13:00:00")],
        })

        with patch.object(exchange, "_CLIENT", client):
            result = exchange.convert_currency.func(
                amount=Decimal("100"),
                source_currency="USD",
                target_currency="EUR",
            )

        self.assertEqual(result["status"], "error")
        self.assertIn("mesma data", result["message"])

    def test_should_return_controlled_error_when_ptax_is_unavailable(self):
        client = FakePtaxClient(error=PtaxClientError("offline"))

        with patch.object(exchange, "_CLIENT", client):
            result = exchange.get_exchange_rate.func(currency="USD")

        self.assertEqual(result["status"], "error")
        self.assertIn("Banco Central", result["message"])


class TestPtaxClient(unittest.TestCase):
    def test_should_request_period_and_keep_only_closing_bulletins(self):
        response = BytesIO(
            b"""{
                "value": [
                    {
                        "cotacaoCompra": 5.00,
                        "cotacaoVenda": 5.01,
                        "dataHoraCotacao": "2026-07-20 10:00:00",
                        "tipoBoletim": "Abertura"
                    },
                    {
                        "cotacaoCompra": 5.10,
                        "cotacaoVenda": 5.11,
                        "dataHoraCotacao": "2026-07-20 13:00:00",
                        "tipoBoletim": "Fechamento"
                    }
                ]
            }"""
        )

        with patch.object(ptax, "urlopen", return_value=response) as urlopen:
            rates = PtaxClient().closing_rates(
                "USD",
                date(2026, 7, 20),
                date(2026, 7, 20),
            )

        requested_url = urlopen.call_args.args[0].full_url
        self.assertIn("@moeda='USD'", requested_url)
        self.assertIn("@dataInicial='07-20-2026'", requested_url)
        self.assertIn("$orderby=dataHoraCotacao%20asc", requested_url)
        self.assertNotIn("%24", requested_url)
        self.assertEqual(len(rates), 1)
        self.assertEqual(rates[0]["bulletin"], "Fechamento")
        self.assertEqual(rates[0]["sell"], Decimal("5.11"))


if __name__ == "__main__":
    unittest.main()
