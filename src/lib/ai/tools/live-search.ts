import type { LiveSearchResult } from "@/lib/types";

interface XAISearchResponse {
  results?: Array<{
    title?: string;
    url?: string;
    snippet?: string;
  }>;
}

export async function liveSearch(
  apiKey: string,
  query: string
): Promise<LiveSearchResult[]> {
  const response = await fetch("https://api.x.ai/v1/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      query,
      data_sources: ["x"],
      search_depth: "advanced",
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`X.ai API error: ${response.status} - ${error}`);
  }

  const data: XAISearchResponse = await response.json();

  if (!data.results) {
    return [];
  }

  return data.results.map((result) => ({
    title: result.title || "N/A",
    url: result.url || "N/A",
    snippet: result.snippet || "N/A",
  }));
}

export function formatLiveResults(results: LiveSearchResult[], query: string): string {
  if (results.length === 0) {
    return `No results found from Live Search for "${query}"`;
  }

  let formatted = `Live search results for "${query}":\n\n`;

  for (const result of results) {
    formatted += `Title: ${result.title}\n`;
    formatted += `URL: ${result.url}\n`;
    formatted += `Snippet: ${result.snippet}\n\n`;
  }

  return formatted.trim();
}
