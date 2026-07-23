import json
from datetime import date, datetime
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


PTAX_BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"
PTAX_SOURCE_URL = "https://dadosabertos.bcb.gov.br/dataset/taxas-de-cambio-todos-os-boletins-diarios"


class PtaxClientError(RuntimeError):
    pass


class PtaxClient:
    def __init__(self, timeout: float = 10):
        self.timeout = timeout

    def list_currencies(self) -> list[dict]:
        payload = self._get(
            "Moedas",
            {
                "$format": "json",
                "$orderby": "simbolo asc",
                "$top": "200",
            },
        )
        return [
            {
                "code": item["simbolo"],
                "name": item["nomeFormatado"],
                "type": item["tipoMoeda"],
            }
            for item in payload
        ]

    def closing_rates(self, currency: str, start_date: date, end_date: date) -> list[dict]:
        days = (end_date - start_date).days + 1
        payload = self._get(
            "CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,"
            "dataFinalCotacao=@dataFinalCotacao)",
            {
                "@moeda": f"'{currency}'",
                "@dataInicial": f"'{self._format_date(start_date)}'",
                "@dataFinalCotacao": f"'{self._format_date(end_date)}'",
                "$format": "json",
                "$orderby": "dataHoraCotacao asc",
                "$top": str(min(days * 5, 2000)),
            },
        )
        return [
            {
                "currency": currency,
                "buy": Decimal(str(item["cotacaoCompra"])),
                "sell": Decimal(str(item["cotacaoVenda"])),
                "quoted_at": item["dataHoraCotacao"],
                "bulletin": item["tipoBoletim"],
            }
            for item in payload
            if item["tipoBoletim"] == "Fechamento"
        ]

    def _get(self, resource: str, params: dict[str, str]) -> list[dict]:
        query = urlencode(params, safe="$'@", quote_via=quote)
        url = f"{PTAX_BASE_URL}/{resource}?{query}"
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Assessor.AI/1.0",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise PtaxClientError("Falha ao consultar o serviço PTAX.") from error

        values = body.get("value")
        if not isinstance(values, list):
            raise PtaxClientError("Resposta inválida do serviço PTAX.")
        return values

    @staticmethod
    def _format_date(value: date) -> str:
        return value.strftime("%m-%d-%Y")


def quote_date(rate: dict) -> date:
    return datetime.fromisoformat(rate["quoted_at"]).date()
