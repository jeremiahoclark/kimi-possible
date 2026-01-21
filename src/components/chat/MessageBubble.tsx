"use client";

import type { Message } from "@/lib/types";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-purple-600 text-white"
            : "bg-[#1a1a1a] text-gray-200 border border-gray-800"
        }`}
      >
        {/* Tool calls indicator */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mb-2 pb-2 border-b border-gray-700">
            <div className="text-xs text-purple-400 mb-1">Tools used:</div>
            <div className="flex flex-wrap gap-1">
              {message.toolCalls.map((tool) => (
                <span
                  key={tool.id}
                  className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-purple-900/50 text-purple-300"
                >
                  {tool.name.replace("_", " ")}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Message content with basic markdown-like rendering */}
        <div className="whitespace-pre-wrap break-words">
          {message.content.split("\n").map((line, i) => {
            // Bold text
            const boldProcessed = line.replace(
              /\*\*(.*?)\*\*/g,
              '<strong class="font-semibold">$1</strong>'
            );
            // Links
            const linkProcessed = boldProcessed.replace(
              /\[([^\]]+)\]\(([^)]+)\)/g,
              '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-purple-400 hover:underline">$1</a>'
            );

            return (
              <span key={i}>
                <span dangerouslySetInnerHTML={{ __html: linkProcessed }} />
                {i < message.content.split("\n").length - 1 && <br />}
              </span>
            );
          })}
        </div>

        {/* Timestamp */}
        <div
          className={`text-xs mt-2 ${
            isUser ? "text-purple-200" : "text-gray-500"
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
}
