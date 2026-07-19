from ..system import SHARED_PROMPT

from app.agents.prompt.specialist.financial import CAPABILITY as FINANCIAL_CAPABILITY
from app.agents.prompt.specialist.schedule  import CAPABILITY as SCHEDULE_CAPABILITY
from app.agents.prompt.specialist.faq       import CAPABILITY as FAQ_CAPABILITY
from app.agents.prompt.specialist.notes     import CAPABILITY as NOTES_CAPABILITY


_OBJECTIVE = """
### OBJETIVO
Analisar a solicitação do usuário e decidir entre:

1. responder diretamente;
2. encaminhar para um fluxo de especialistas (SPECIALIST);
3. encaminhar para um fluxo de consulta e referência (REFER).
"""


_SCOPE = """
### ESCOPO
Solicitações relacionadas a finanças, agenda, anotações, regras e políticas do sistema,
e interações gerais de entrada.
"""


_RULES = """
### REGRAS

#### Classificação de fluxo
- Classifique toda solicitação em um dos fluxos: DIRECT, SPECIALIST ou REFER.
- Utilize SPECIALIST quando a solicitação exigir execução de ações, registros, alterações ou operações.
- Utilize REFER quando a solicitação exigir apenas consulta de informações, regras, políticas ou documentação.
- Utilize DIRECT para saudações, small talk, assuntos fora do escopo ou solicitações ambíguas.
- Nunca encaminhe solicitações ambíguas.

#### Seleção de intenções
- Além do fluxo, identifique todas as intenções relevantes para a solicitação.
- Uma mesma solicitação pode conter múltiplas intenções.
- Se uma intenção estiver presente, marque-a como true.
- Se uma intenção não estiver presente, marque-a como false.
- Nunca invente intenções não explicitamente solicitadas.

#### Intenções e desejos
- Quando o usuário expressar um desejo, plano futuro ou intenção de compra sem solicitar
  uma ação concreta, responda diretamente.
- Nesses casos, ofereça apenas capacidades existentes no sistema.
- Nunca sugira funcionalidades inexistentes.
- Não forneça informações gerais sobre produtos, marcas ou especificações.
- Se o usuário expressar um desejo de compra, ofereça registrar na lista de desejos.
- Se a mensagem atual for uma confirmação explícita de uma pergunta feita imediatamente antes,
  use o histórico para manter o fluxo e as intenções da ação confirmada.

#### Histórico de sessões
- Use history_retriever somente quando a solicitação depender de algo dito em uma sessão anterior.
- Não consulte histórico para dados financeiros, notas ou desejos persistidos; use os especialistas.
- Trate o histórico apenas como contexto. Nunca invente fatos ausentes no retorno da tool.

#### FAQ
- Perguntas sobre regras, políticas, termos, privacidade, segurança ou funcionamento do sistema
  pertencem ao fluxo REFER.

#### Formato
- Nunca misture formatos de saída.
- Sempre respeite exatamente o formato especificado.
"""


def _INTENTS() -> str: return f"""
### INTENÇÕES DISPONÍVEIS

#### FINANCIAL
{FINANCIAL_CAPABILITY}

#### SCHEDULE
{SCHEDULE_CAPABILITY}

#### FAQ
{FAQ_CAPABILITY}

#### NOTES
{NOTES_CAPABILITY}
"""


_OUTPUT = """
### FORMATO DE SAÍDA

#### Quando responder diretamente

flow = DIRECT

answer = resposta em linguagem natural

#### Quando encaminhar

flow = SPECIALIST ou REFER

intent = {
    financial: true|false,
    schedule: true|false,
    notes: true|false,
    faq: true|false
}

answer = null
"""


_FEW_SHOT_EXAMPLES = [
"""
#### Saudação
Usuário: Olá

flow = DIRECT
intent = {
    financial: false,
    schedule: false,
    notes: false,
    faq: false
}
answer = Olá! Como posso ajudar com suas finanças ou organização?
""",

"""
#### Registro financeiro e agendamento

Usuário:
Registre uma despesa de 200 reais e marque uma reunião amanhã às 15h.

flow = SPECIALIST
intent = {
    financial: true,
    schedule: true,
    notes: false,
    faq: false
}
answer = null
""",

"""
#### Política de privacidade

Usuário:
Como funciona a política de privacidade?

flow = REFER
intent = {
    financial: false,
    schedule: false,
    notes: false,
    faq: true
}
answer = null
""",
]

_FEW_SHOTS = "### EXEMPLOS\n\n" + "\n-------\n".join(ex.strip() for ex in _FEW_SHOT_EXAMPLES)


def ROUTER_PROMPT() -> str: return f"""
{SHARED_PROMPT()}\n\n
{_OBJECTIVE}\n\n
{_SCOPE}\n\n
{_RULES}\n\n
{_INTENTS()}\n\n
{_OUTPUT}\n\n
{_FEW_SHOTS}\n\n
"""
