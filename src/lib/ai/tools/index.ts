import type { ToolDefinition, Env } from "@/lib/types";
import { exaSearch, formatExaResults } from "./exa-search";
import { liveSearch, formatLiveResults } from "./live-search";
import { youtubeSearch, formatYouTubeResults } from "./youtube-search";

// Tool definitions for the OpenRouter API
export const tools: ToolDefinition[] = [
  {
    type: "function",
    function: {
      name: "exa_search",
      description: "Perform a web search using Exa.ai for recent and relevant information from across the web.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "The search query to find information on the web.",
          },
        },
        required: ["query"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "live_search",
      description: "Perform a live search on X (formerly Twitter) using x.ai's Live Search API for real-time social media content.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "The search query for X/Twitter content.",
          },
        },
        required: ["query"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "youtube_search",
      description: "Search YouTube for videos related to a topic. Returns video titles, channels, and descriptions.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "The search query for YouTube videos.",
          },
          max_results: {
            type: "string",
            description: "Maximum number of results to return (1-50). Default is 5.",
          },
        },
        required: ["query"],
      },
    },
  },
];

// Tool executor - dispatches to the appropriate tool function
export async function executeTool(
  toolName: string,
  args: Record<string, unknown>,
  env: Env
): Promise<string> {
  switch (toolName) {
    case "exa_search": {
      const query = args.query as string;
      if (!env.EXA_API_KEY) {
        return "Error: EXA_API_KEY not configured.";
      }
      try {
        const results = await exaSearch(env.EXA_API_KEY, query);
        return formatExaResults(results, query);
      } catch (error) {
        return `Error performing Exa search: ${error instanceof Error ? error.message : String(error)}`;
      }
    }

    case "live_search": {
      const query = args.query as string;
      if (!env.X_API_KEY) {
        return "Error: X_API_KEY not configured.";
      }
      try {
        const results = await liveSearch(env.X_API_KEY, query);
        return formatLiveResults(results, query);
      } catch (error) {
        return `Error performing Live search: ${error instanceof Error ? error.message : String(error)}`;
      }
    }

    case "youtube_search": {
      const query = args.query as string;
      const maxResults = parseInt(args.max_results as string) || 5;
      if (!env.YOUTUBE_API_KEY) {
        return "Error: YOUTUBE_API_KEY not configured.";
      }
      try {
        const results = await youtubeSearch(env.YOUTUBE_API_KEY, query, maxResults);
        return formatYouTubeResults(results, query);
      } catch (error) {
        return `Error performing YouTube search: ${error instanceof Error ? error.message : String(error)}`;
      }
    }

    default:
      return `Error: Unknown tool "${toolName}"`;
  }
}
