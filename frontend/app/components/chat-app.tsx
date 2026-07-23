import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router";

import {
  ArrowUpIcon,
  ChevronDownIcon,
  CodeIcon,
  CompassIcon,
  MenuIcon,
  MoreIcon,
  PanelLeftIcon,
  PaperclipIcon,
  PenIcon,
  PlusIcon,
  SearchIcon,
  SparklesIcon,
  UserIcon,
} from "./icons";

type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

const conversations = [
  { id: "planejamento-semanal", title: "Planejamento da semana" },
  { id: "resumo-documento", title: "Resumo de documento" },
  { id: "ideias-apresentacao", title: "Ideias para apresentação" },
];

const suggestions = [
  {
    icon: PenIcon,
    title: "Escrever um texto",
    prompt: "Me ajude a escrever um texto claro e objetivo",
  },
  {
    icon: CompassIcon,
    title: "Planejar uma ideia",
    prompt: "Quero estruturar e planejar uma nova ideia",
  },
  {
    icon: CodeIcon,
    title: "Explicar um conceito",
    prompt: "Explique um conceito complexo de forma simples",
  },
  {
    icon: SparklesIcon,
    title: "Gerar sugestões",
    prompt: "Gere sugestões criativas para o meu projeto",
  },
];

export function ChatApp() {
  const { chatId } = useParams();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const conversationTitle =
    conversations.find((conversation) => conversation.id === chatId)?.title ??
    "Nova conversa";

  useEffect(() => {
    setMessages([]);
    setMessage("");
    setSidebarOpen(false);
  }, [chatId]);

  function resizeTextarea() {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "0px";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  }

  function submitMessage() {
    const content = message.trim();
    if (!content) return;

    setMessages((current) => [
      ...current,
      { id: Date.now(), role: "user", content },
      {
        id: Date.now() + 1,
        role: "assistant",
        content:
          "Esta é uma demonstração da interface. Quando o backend for conectado, a resposta da IA aparecerá aqui.",
      },
    ]);
    setMessage("");
    requestAnimationFrame(() => {
      if (textareaRef.current) textareaRef.current.style.height = "24px";
      textareaRef.current?.focus();
    });
  }

  return (
    <div className="chat-shell">
      <a className="skip-link" href="#chat-content">
        Pular para a conversa
      </a>

      {sidebarOpen && (
        <button
          className="sidebar-backdrop"
          type="button"
          aria-label="Fechar menu lateral"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`sidebar ${sidebarOpen ? "sidebar--open" : ""}`}
        aria-label="Navegação das conversas"
      >
        <div className="sidebar__header">
          <Link className="brand" to="/" aria-label="Assessor, página inicial">
            <span className="brand__mark" aria-hidden="true">
              A
            </span>
            <span>Assessor</span>
          </Link>
          <button
            className="icon-button sidebar__close"
            type="button"
            aria-label="Fechar menu lateral"
            onClick={() => setSidebarOpen(false)}
          >
            <PanelLeftIcon />
          </button>
        </div>

        <nav className="sidebar__navigation">
          <Link className="sidebar-action sidebar-action--primary" to="/">
            <PlusIcon />
            <span>Nova conversa</span>
            <span className="shortcut" aria-hidden="true">
              ⌘ K
            </span>
          </Link>
          <button className="sidebar-action" type="button">
            <SearchIcon />
            <span>Buscar conversas</span>
          </button>
        </nav>

        <div className="conversation-list">
          <p className="conversation-list__label">Recentes</p>
          {conversations.map((conversation) => (
            <Link
              className={`conversation ${
                chatId === conversation.id ? "conversation--active" : ""
              }`}
              key={conversation.id}
              to={`/chat/${conversation.id}`}
            >
              <span>{conversation.title}</span>
              <MoreIcon />
            </Link>
          ))}
        </div>

        <div className="sidebar__footer">
          <button className="profile" type="button">
            <span className="profile__avatar">
              <UserIcon />
            </span>
            <span className="profile__content">
              <strong>Davi Alves</strong>
              <small>Plano pessoal</small>
            </span>
            <MoreIcon />
          </button>
        </div>
      </aside>

      <main className="chat-main" id="chat-content">
        <header className="topbar">
          <button
            className="icon-button topbar__menu"
            type="button"
            aria-label="Abrir menu lateral"
            aria-expanded={sidebarOpen}
            onClick={() => setSidebarOpen(true)}
          >
            <MenuIcon />
          </button>
          <button className="model-selector" type="button">
            <span>Assessor</span>
            <span className="model-selector__version">IA</span>
            <ChevronDownIcon />
          </button>
          <button className="avatar-button" type="button" aria-label="Abrir perfil">
            DA
          </button>
        </header>

        <section
          className={`chat-content ${
            messages.length > 0 ? "chat-content--conversation" : ""
          }`}
          aria-labelledby="chat-title"
        >
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state__mark" aria-hidden="true">
                <SparklesIcon />
              </div>
              <h1 id="chat-title">
                {chatId ? conversationTitle : "Como posso ajudar hoje?"}
              </h1>
              <p>
                Converse, crie e explore ideias. Seu assistente está pronto para
                começar.
              </p>

              <div className="suggestions" aria-label="Sugestões de perguntas">
                {suggestions.map(({ icon: SuggestionIcon, title, prompt }) => (
                  <button
                    key={title}
                    className="suggestion-card"
                    type="button"
                    onClick={() => {
                      setMessage(prompt);
                      textareaRef.current?.focus();
                    }}
                  >
                    <SuggestionIcon />
                    <span>{title}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div
              className="message-list"
              role="log"
              aria-live="polite"
              aria-label="Mensagens da conversa"
            >
              <h1 className="sr-only" id="chat-title">
                {conversationTitle}
              </h1>
              {messages.map((item) => (
                <article
                  className={`message message--${item.role}`}
                  key={item.id}
                >
                  <div className="message__avatar" aria-hidden="true">
                    {item.role === "user" ? "DA" : <SparklesIcon />}
                  </div>
                  <div>
                    <strong>{item.role === "user" ? "Você" : "Assessor"}</strong>
                    <p>{item.content}</p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <div className="composer-area">
          <form
            className="composer"
            onSubmit={(event) => {
              event.preventDefault();
              submitMessage();
            }}
          >
            <textarea
              ref={textareaRef}
              rows={1}
              value={message}
              aria-label="Mensagem para o Assessor"
              placeholder="Pergunte alguma coisa"
              onChange={(event) => {
                setMessage(event.target.value);
                resizeTextarea();
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  submitMessage();
                }
              }}
            />
            <div className="composer__actions">
              <button
                className="composer__attach"
                type="button"
                aria-label="Anexar arquivo"
              >
                <PaperclipIcon />
              </button>
              <span className="composer__hint">Enter para enviar</span>
              <button
                className="composer__send"
                type="submit"
                aria-label="Enviar mensagem"
                disabled={!message.trim()}
              >
                <ArrowUpIcon />
              </button>
            </div>
          </form>
          <p className="disclaimer">
            O Assessor pode cometer erros. Confira informações importantes.
          </p>
        </div>
      </main>
    </div>
  );
}
