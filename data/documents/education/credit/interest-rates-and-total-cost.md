# Juros, capitalização e Custo Efetivo Total

Juros são a remuneração pelo uso do dinheiro ao longo do tempo. Para quem toma crédito, representam parte do custo da dívida. Para quem aplica recursos, representam parte da remuneração recebida, sujeita às condições e aos riscos do produto.

## Taxa e período

Toda taxa está associada a um período. Uma taxa de 2% ao mês não é diretamente comparável a uma taxa de 24% ao ano sem considerar a forma de capitalização.

Uma taxa proporcional apenas multiplica períodos. Uma taxa equivalente considera a incidência acumulada dos juros:

```text
taxa anual equivalente = (1 + taxa mensal)¹² - 1
```

Uma taxa de 2% ao mês equivale aproximadamente a 26,82% ao ano:

```text
(1 + 0,02)¹² - 1 = 0,2682
```

## Juros simples

Nos juros simples, os juros de cada período são calculados apenas sobre o capital inicial:

```text
juros = capital × taxa × períodos
montante = capital + juros
```

Para R$ 1.000 a 2% ao mês durante 6 meses:

```text
juros = 1.000 × 0,02 × 6 = 120
montante = 1.120
```

## Juros compostos

Nos juros compostos, os juros de cada período são incorporados ao saldo. Os períodos seguintes calculam juros sobre o capital e sobre juros acumulados:

```text
montante = capital × (1 + taxa)ᵖᵉʳíᵒᵈᵒˢ
```

Para R$ 1.000 a 2% ao mês durante 6 meses:

```text
montante = 1.000 × (1,02)⁶
montante ≈ 1.126,16
```

O crescimento não é linear. Quanto maiores a taxa e o prazo, maior a diferença entre juros simples e compostos.

## Valor da parcela e custo total

Uma parcela menor não significa necessariamente crédito mais barato. Prazo maior pode reduzir a prestação mensal e aumentar o total pago.

Exemplo:

| Proposta | Parcelas | Total pago |
|---|---:|---:|
| A | 12 × R$ 550 | R$ 6.600 |
| B | 24 × R$ 310 | R$ 7.440 |

A proposta B exige menos dinheiro por mês, mas custa R$ 840 a mais no total. A decisão também depende de tarifas, seguros, tributos, entrada, data dos pagamentos e capacidade de pagamento.

## Custo Efetivo Total

O Custo Efetivo Total, ou CET, reúne os encargos e despesas de uma operação de crédito. Ele inclui a taxa de juros e pode incluir tarifas, tributos, seguros e outros valores cobrados.

O CET deve ser informado como taxa percentual anual antes da contratação. Duas ofertas com a mesma taxa nominal podem ter CETs diferentes porque seus custos adicionais são diferentes.

Uma comparação de crédito considera, no mínimo:

- CET anual;
- valor liberado ao cliente;
- valor e quantidade de parcelas;
- total a pagar;
- datas de vencimento;
- garantias exigidas;
- consequências do atraso;
- condições de quitação antecipada.

## Taxa nominal, taxa real e inflação

A rentabilidade nominal mostra a variação do dinheiro em moeda corrente. A rentabilidade real considera a inflação do período:

```text
rentabilidade real = (1 + rentabilidade nominal) / (1 + inflação) - 1
```

Se um investimento rende 10% e a inflação do período é 6%, a rentabilidade real é aproximadamente 3,77%, antes de impostos e custos:

```text
(1,10 / 1,06) - 1 ≈ 0,0377
```

Subtrair diretamente 10% menos 6% produz uma aproximação, não o cálculo exato.

## Referências

- Banco Central do Brasil. [Entenda os juros](https://www.bcb.gov.br/cidadaniafinanceira/entendajuro/1000).
- Banco Central do Brasil. [Caderno de Educação Financeira](https://www.bcb.gov.br/pre/pef/port/caderno_cidadania_financeira.pdf).
- Comissão de Valores Mobiliários. [Calculadora do Investidor](https://www.gov.br/investidor/pt-br/ferramentas/calculadora-do-investidor).

Fontes consultadas em 23 de julho de 2026.
