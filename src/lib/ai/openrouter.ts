import type { OpenRouterMessage, OpenRouterResponse, ToolDefinition } from "@/lib/types";

const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions";
const MODEL = "moonshotai/kimi-k2";

export interface ChatCompletionOptions {
  messages: OpenRouterMessage[];
  tools?: ToolDefinition[];
  temperature?: number;
}

export async function createChatCompletion(
  apiKey: string,
  options: ChatCompletionOptions
): Promise<OpenRouterResponse> {
  const { messages, tools, temperature = 0.3 } = options;

  const response = await fetch(OPENROUTER_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
      "HTTP-Referer": "https://github.com/kingj/kimi-possible",
      "X-Title": "Kimi Possible",
    },
    body: JSON.stringify({
      model: MODEL,
      messages,
      tools,
      temperature,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenRouter API error: ${response.status} - ${error}`);
  }

  return response.json();
}
