from app.workflow.flow import assessor_flow

while 1:
    try:
        user_input = input("Digite sua pergunta: ").strip()
        if user_input.lower() in ("killmyself"):
            print("Encerrando o assistente.")
            break

        resposta = assessor_flow(pergunta_usuario=user_input, session_id="id_usuario_mas_agora_não_importa")
        print("🤖 > " + resposta + "\n")
    except Exception as e:
        print(f'Erro: {e}')