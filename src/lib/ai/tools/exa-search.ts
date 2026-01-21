import type { ExaSearchResult } from "@/lib/types";

interface ExaApiResponse {
  results: Array<{
    title: string;
    url: string;
    text: string;
  }>;
}

export async function exaSearch(
  apiKey: string,
  query: string
): Promise<ExaSearchResult[]> {
  const response = await fetch("https://api.exa.ai/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify({
      query,
      useAutoprompt: true,
      numResults: 3,
      contents: {
        text: {
          includeHtmlTags: false,
        },
      },
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Exa API error: ${response.status} - ${error}`);
  }

  const data: ExaApiResponse = await response.json();

  return data.results.map((result) => ({
    title: result.title,
    url: result.url,
    text: result.text,
  }));
}

export function formatExaResults(results: ExaSearchResult[], query: string): string {
  if (results.length === 0) {
    return `No results found for "${query}"`;
  }

  let formatted = `Search results for "${query}":\n\n`;

  for (const result of results) {
    formatted += `Title: ${result.title}\n`;
    formatted += `URL: ${result.url}\n`;
    formatted += `Content: ${result.text}\n`;
    formatted += "-".repeat(20) + "\n";
  }

  return formatted;
}
