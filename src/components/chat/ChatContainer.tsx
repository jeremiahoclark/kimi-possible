"use client";

import { useChat } from "@/hooks/useChat";
import { DomainSelector } from "./DomainSelector";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";

export function ChatContainer() {
  const { messages, domain, setDomain, sendMessage, isLoading, error } = useChat();

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">&#128373;&#65039;&#8205;&#9792;&#65039;</span>
            <div>
              <h1 className="text-lg font-semibold text-white">Kimi Possible</h1>
              <p className="text-xs text-gray-500">AI Research Assistant</p>
            </div>
          </div>
          <DomainSelector value={domain} onChange={setDomain} />
        </div>
      </header>

      {/* Error banner */}
      {error && (
        <div className="bg-red-900/50 border-b border-red-800 px-4 py-2">
          <p className="text-sm text-red-300 text-center">{error}</p>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-hidden max-w-4xl w-full mx-auto flex flex-col">
        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
