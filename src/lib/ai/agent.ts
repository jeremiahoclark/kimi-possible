import type { Domain, Env, Message, OpenRouterMessage, ToolCall } from "@/lib/types";
import { createChatCompletion } from "./openrouter";
import { tools, executeTool } from "./tools";
import { getSystemPrompt } from "./prompts";

const MAX_ITERATIONS = 5;

interface AgentResult {
  content: string;
  toolCalls: ToolCall[];
}

export async function runAgent(
  messages: Message[],
  domain: Domain,
  env: Env
): Promise<AgentResult> {
  // Build conversation history for the API
  const conversationHistory: OpenRouterMessage[] = [
    { role: "system", content: getSystemPrompt(domain) },
    ...messages.map((msg) => ({
      role: msg.role as "user" | "assistant",
      content: msg.content,
    })),
  ];

  const allToolCalls: ToolCall[] = [];
  let iteration = 0;
  let continueLoop = true;

  while (iteration < MAX_ITERATIONS && continueLoop) {
    iteration++;

    const response = await createChatCompletion(env.OPENROUTER_API_KEY, {
      messages: conversationHistory,
      tools,
      temperature: 0.3,
    });

    const choice = response.choices[0];
    const finishReason = choice.finish_reason;

    if (finishReason === "tool_calls" && choice.message.tool_calls) {
      // Add assistant message with tool calls to history
      conversationHistory.push({
        role: "assistant",
        content: choice.message.content || "",
        tool_calls: choice.message.tool_calls,
      });

      // Execute each tool call
      for (const toolCall of choice.message.tool_calls) {
        const args = JSON.parse(toolCall.function.arguments);
        const result = await executeTool(toolCall.function.name, args, env);

        // Track tool calls for response
        allToolCalls.push({
          id: toolCall.id,
          name: toolCall.function.name,
          arguments: args,
          result,
        });

        // Add tool result to conversation
        conversationHistory.push({
          role: "tool",
          tool_call_id: toolCall.id,
          name: toolCall.function.name,
          content: JSON.stringify({ result }),
        });
      }
    } else {
      // Final response
      return {
        content: choice.message.content || "",
        toolCalls: allToolCalls,
      };
    }
  }

  // Max iterations reached
  return {
    content: "I've reached the maximum number of tool calls. Here's what I found so far based on my research.",
    toolCalls: allToolCalls,
  };
}
