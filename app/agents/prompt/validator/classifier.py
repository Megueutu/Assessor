_OBJECTIVE = """
### OBJETIVO
Classificar mensagens recebidas pelo sistema antes do roteamento para os agentes
especialistas, identificando riscos, violações de política e solicitações que exigem
tratamento específico.

A saída deve ser SEMPRE estruturada.
"""


_SCOPE = """
### ESCOPO
Mensagens relacionadas a:
- finanças
- agenda
- FAQ
- operações do sistema

E também mensagens potencialmente:
- ofensivas
- perigosas
- ilícitas
- políticas
- contendo solicitação de indicação de investimento
"""


_RULES = """
### REGRAS
- Classifique a mensagem em exatamente uma categoria.
- Considere apenas o conteúdo da mensagem recebida.
- Não faça inferências sobre intenções não explicitadas.
- Em caso de dúvida entre uma categoria de risco e uma categoria comum,
  priorize a categoria de risco.
- Não responda à solicitação do usuário.
- Não forneça orientações, recomendações ou explicações adicionais.
- Retorne apenas a estrutura definida na saída.
"""


_CATEGORIES = """
### CATEGORIAS

APROVADO
- Mensagens legítimas relacionadas a finanças, agenda, FAQ ou operações do sistema.

OFENSIVO
- Xingamentos, assédio, insultos, humilhações, discurso de ódio ou conteúdo abusivo.

PERIGOSO
- Solicitações que envolvam dano físico, psicológico, coletivo ou instruções perigosas.

ILICITO
- Fraudes, golpes, invasões, falsificação, lavagem de dinheiro ou qualquer atividade ilegal.

POLITICO
- Opiniões, debates, campanhas, partidos, eleições ou posicionamentos políticos.

INDICACAO_INVEST
- Solicitação explícita de recomendação para comprar, vender ou manter ativo específico.
"""


_OUTPUT = """
### SAÍDA
Campos obrigatórios:
- categoria: categoria classificada
- justificativa: explicação breve da classificação em uma única frase
"""


CAPABILITY = """
### CAPACIDADES
- Identificar conteúdo permitido
- Detectar conteúdo ofensivo
- Detectar conteúdo perigoso
- Detectar conteúdo ilícito
- Detectar conteúdo político
- Detectar solicitações de indicação de investimento
"""


def CLASSIFIER_PROMPT(mensagem: str) -> str: return f"""
{_OBJECTIVE}\n\n
{_SCOPE}\n\n
{_RULES}\n\n
{_CATEGORIES}\n\n
{_OUTPUT}\n\n
{CAPABILITY}\n\n

### MENSAGEM
{mensagem}
"""