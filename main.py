from app.workflow.flow import assessor_flow

BREAKWAYS = ('exit', 'quit', 'close', 'encerrar')

def main():
    try:
        message = input("😎 > ").strip()
        if message.lower() in BREAKWAYS:
            print("\nEncerrando a conversa.")
            return
        
        answer = assessor_flow(pergunta_usuario=message, session_id="id_usuario_mas_agora_não_importa")
        print("🤖 > " + answer + "\n")
    
    except Exception as e:
        print(f'Erro: {e}')

print(f'\nAssessor iniciado! Digite: ("{'", "'.join(BREAKWAYS)}") para encerrar.')

while 1:
    main()