import type { YouTubeSearchResult } from "@/lib/types";

interface YouTubeApiResponse {
  items?: Array<{
    id: {
      videoId?: string;
      channelId?: string;
      playlistId?: string;
    };
    snippet: {
      title: string;
      description: string;
      channelTitle: string;
      publishedAt: string;
      thumbnails: {
        default?: { url: string };
        medium?: { url: string };
        high?: { url: string };
      };
    };
  }>;
  error?: {
    message: string;
  };
}

export async function youtubeSearch(
  apiKey: string,
  query: string,
  maxResults: number = 5
): Promise<YouTubeSearchResult[]> {
  const params = new URLSearchParams({
    part: "snippet",
    q: query,
    type: "video",
    maxResults: String(Math.min(maxResults, 50)),
    key: apiKey,
  });

  const response = await fetch(
    `https://www.googleapis.com/youtube/v3/search?${params.toString()}`
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`YouTube API error: ${response.status} - ${error}`);
  }

  const data: YouTubeApiResponse = await response.json();

  if (data.error) {
    throw new Error(`YouTube API error: ${data.error.message}`);
  }

  if (!data.items) {
    return [];
  }

  return data.items
    .filter((item) => item.id.videoId)
    .map((item) => ({
      title: item.snippet.title,
      videoId: item.id.videoId!,
      channelTitle: item.snippet.channelTitle,
      description: item.snippet.description,
      publishedAt: item.snippet.publishedAt,
      thumbnailUrl: item.snippet.thumbnails.medium?.url ||
                    item.snippet.thumbnails.default?.url || "",
    }));
}

export function formatYouTubeResults(results: YouTubeSearchResult[], query: string): string {
  if (results.length === 0) {
    return `No YouTube videos found for "${query}"`;
  }

  let formatted = `YouTube search results for "${query}":\n\n`;

  for (const result of results) {
    formatted += `Title: ${result.title}\n`;
    formatted += `Channel: ${result.channelTitle}\n`;
    formatted += `URL: https://www.youtube.com/watch?v=${result.videoId}\n`;
    formatted += `Published: ${new Date(result.publishedAt).toLocaleDateString()}\n`;
    formatted += `Description: ${result.description.slice(0, 200)}${result.description.length > 200 ? "..." : ""}\n`;
    formatted += "-".repeat(20) + "\n";
  }

  return formatted;
}
