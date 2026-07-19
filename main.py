from app.workflow.startup import validate_api_keys

BREAKWAYS = ("exit", "quit", "close", "encerrar", "sair")

def main():
    validation = validate_api_keys()
    print(
        f"APIs validadas: Gemini e {validation.valid_groq_keys} chave(s) Groq válida(s)."
    )
    if validation.invalid_groq_keys:
        print(f"Chaves Groq ignoradas: {', '.join(validation.invalid_groq_keys)}.")

    from app.database.sessions import save, start, terminate
    from app.workflow.flow import assessor_flow

    breakways = '", "'.join(BREAKWAYS)
    print(f'\nAssessor iniciado! Digite: "{breakways}" para encerrar.')
    session_id = "id_usuario"
    start(session_id)

    try:
        while True:
            try:
                message = input("😎 > ").strip()
                if message.lower() in BREAKWAYS:
                    print("🐳 > Encerrando a conversa.")
                    break

                save(session_id, "human", message)
                answer = assessor_flow(message, session_id=session_id)
                save(session_id, "assistant", answer)

                if answer == "{}":
                    print(f"⚠️ > Nenhuma resposta disponível.\n")
                else:
                    print(f"🤖 > {answer}\n")

            except KeyboardInterrupt:
                print("\n🐳 > Encerrando a conversa.")
                break

            except Exception as e:
                print(f"🐛 > {e}\n")
    finally:
        try:
            terminate(session_id)
        except Exception as e:
            print(f"🐛 > Não foi possível encerrar a sessão: {e}\n")

if __name__ == "__main__":
    main()
