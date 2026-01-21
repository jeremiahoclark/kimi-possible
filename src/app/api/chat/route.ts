import { NextRequest, NextResponse } from "next/server";
import { runAgent } from "@/lib/ai/agent";
import type { ChatRequest, Env, Message } from "@/lib/types";
import { getCloudflareContext } from "@opennextjs/cloudflare";

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json();
    const { messages, domain } = body;

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: "Messages array is required" },
        { status: 400 }
      );
    }

    // Get environment variables from Cloudflare context
    const ctx = await getCloudflareContext();
    const cfEnv = ctx.env as Record<string, string>;

    const env: Env = {
      OPENROUTER_API_KEY: cfEnv.OPENROUTER_API_KEY || process.env.OPENROUTER_API_KEY || "",
      EXA_API_KEY: cfEnv.EXA_API_KEY || process.env.EXA_API_KEY || "",
      X_API_KEY: cfEnv.X_API_KEY || process.env.X_API_KEY || "",
      YOUTUBE_API_KEY: cfEnv.YOUTUBE_API_KEY || process.env.YOUTUBE_API_KEY || "",
    };

    if (!env.OPENROUTER_API_KEY) {
      return NextResponse.json(
        { error: "OPENROUTER_API_KEY is not configured" },
        { status: 500 }
      );
    }

    const result = await runAgent(messages, domain || "general", env);

    const responseMessage: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: result.content,
      timestamp: new Date(),
      toolCalls: result.toolCalls.length > 0 ? result.toolCalls : undefined,
    };

    return NextResponse.json({
      message: responseMessage,
      toolCalls: result.toolCalls,
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "An unexpected error occurred" },
      { status: 500 }
    );
  }
}
