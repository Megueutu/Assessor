from app.workflow.flow import assessor_flow


BREAKWAYS = {"exit", "quit", "close", "encerrar", "sair"}


def main():
    print(f'\nAssessor iniciado! Digite: "{'", "'.join(BREAKWAYS)}" para encerrar.')
    session_id = "id_usuario"

    while True:
        try:
            message = input("😎 > ").strip()
            if message.lower() in BREAKWAYS:
                print("\n🐳 > Encerrando a conversa.")
                break

            answer = assessor_flow(message, session_id=session_id)
            print(f"🤖 > {answer}\n")

        except KeyboardInterrupt:
            print("\n🐳 > Encerrando a conversa.")
            break

        except Exception as e:
            print(f"🐛 > {e}\n")

if __name__ == "__main__":
    main()