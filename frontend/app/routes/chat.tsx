import type { Route } from "./+types/chat";
import { ChatApp } from "../components/chat-app";

export function meta({ params }: Route.MetaArgs) {
  return [
    { title: "Conversa — Assessor" },
    {
      name: "description",
      content: `Conversa ${params.chatId ?? ""} no Assessor.`,
    },
  ];
}

export default function Chat() {
  return <ChatApp />;
}
