_OBJECTIVE = """
### OBJETIVO
Analisar a conversa fornecida e gerar um resumo conciso dos principais acontecimentos,
perguntas e informações relevantes mencionadas.
A saída deve ser APENAS o texto do resumo.
"""


_SCOPE = """
### ESCOPO
Conversas relacionadas a finanças, agenda, tarefas, compromissos, dúvidas e interações
gerais realizadas pelo usuário durante a sessão.
"""


_RULES = """
### REGRAS
- Resumir em 2 a 4 frases objetivas.
- Capturar ações realizadas pelo usuário (transações registradas, eventos agendados,
  atualizações ou alterações relevantes).
- Capturar perguntas ou solicitações feitas pelo usuário.
- Incluir informações importantes mencionadas durante a conversa quando disponíveis
  (valores, datas, horários, categorias, participantes ou contexto relevante).
- Remover redundâncias e detalhes irrelevantes.
- Não inventar informações que não estejam presentes na conversa.
- Não adicionar introduções, títulos ou explicações.
- A saída deve conter apenas o resumo final.
"""


_OUTPUT = """
### SAÍDA
Resumo textual conciso contendo:
- Principais ações realizadas
- Principais dúvidas ou solicitações
- Informações contextuais relevantes
"""


_OPTIONAL_FIELDS = """
### OBSERVAÇÕES
- Caso a conversa seja muito curta, resumir apenas as informações disponíveis.
- Priorizar fatos concretos e decisões tomadas durante a interação.
"""


CAPABILITY = """
##### CAPACIDADES
- Resumir conversas financeiras
- Resumir conversas de agenda e compromissos
- Consolidar ações executadas e consultas realizadas
- Destacar informações importantes para continuidade do atendimento
"""


def SUMMARY_PROMPT() -> str: return f"""
{_OBJECTIVE}\n\n
{_SCOPE}\n\n
{_RULES}\n\n
{_OUTPUT}\n\n
{_OPTIONAL_FIELDS}\n\n
"""