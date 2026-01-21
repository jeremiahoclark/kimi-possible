// Domain types for research modes
export type Domain = "general" | "content_research" | "technical_research" | "market_research";

// Message types
export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
}

// Tool call types
export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
  result?: string;
}

// OpenRouter API types
export interface OpenRouterMessage {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  tool_call_id?: string;
  name?: string;
  tool_calls?: OpenRouterToolCall[];
}

export interface OpenRouterToolCall {
  id: string;
  type: "function";
  function: {
    name: string;
    arguments: string;
  };
}

export interface OpenRouterChoice {
  index: number;
  message: OpenRouterMessage & {
    tool_calls?: OpenRouterToolCall[];
  };
  finish_reason: "stop" | "tool_calls" | "length" | null;
}

export interface OpenRouterResponse {
  id: string;
  choices: OpenRouterChoice[];
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

// Tool definition types
export interface ToolDefinition {
  type: "function";
  function: {
    name: string;
    description: string;
    parameters: {
      type: "object";
      properties: Record<string, {
        type: string;
        description: string;
        enum?: string[];
      }>;
      required: string[];
    };
  };
}

// Search result types
export interface ExaSearchResult {
  title: string;
  url: string;
  text: string;
}

export interface LiveSearchResult {
  title: string;
  url: string;
  snippet: string;
}

export interface YouTubeSearchResult {
  title: string;
  videoId: string;
  channelTitle: string;
  description: string;
  publishedAt: string;
  thumbnailUrl: string;
}

// Chat API types
export interface ChatRequest {
  messages: Message[];
  domain: Domain;
}

export interface ChatResponse {
  message: Message;
  toolCalls?: ToolCall[];
}

// Environment bindings for Cloudflare
export interface Env {
  OPENROUTER_API_KEY: string;
  EXA_API_KEY: string;
  X_API_KEY: string;
  YOUTUBE_API_KEY: string;
}
