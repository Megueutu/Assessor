import type { Route } from "./+types/home";
import { ChatApp } from "../components/chat-app";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Assessor — seu assistente de IA" },
    {
      name: "description",
      content: "Converse, crie e explore ideias com o Assessor.",
    },
  ];
}

export default function Home() {
  return <ChatApp />;
}
