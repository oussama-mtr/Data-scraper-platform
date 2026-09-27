import type { HistoryItem, SearchResult, Source } from "../types";

const API_BASE = "/api";

export async function fetchSources(): Promise<Source[]> {
  const response = await fetch(`${API_BASE}/sources`);
  const data = await response.json();
  return data.sources;
}

export async function fetchHistory(): Promise<HistoryItem[]> {
  const response = await fetch(`${API_BASE}/history`);
  const data = await response.json();
  return data.items;
}

export async function fetchDownloads(): Promise<Array<Record<string, unknown>>> {
  const response = await fetch(`${API_BASE}/downloads`);
  const data = await response.json();
  return data.files;
}

export async function fetchResult(searchId: string): Promise<SearchResult> {
  const response = await fetch(`${API_BASE}/results/${searchId}`);
  if (!response.ok) {
    throw new Error("Result not found");
  }
  return response.json();
}

export function getExcelDownloadUrl(searchId: string): string {
  return `${API_BASE}/results/${searchId}/excel`;
}

export function streamSearch(
  query: string,
  onProgress: (event: { stage: string; message: string; progress: number }) => void,
  onResult: (result: SearchResult) => void,
  onError: (message: string) => void,
): () => void {
  const controller = new AbortController();

  fetch(`${API_BASE}/search/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ query }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok || !response.body) {
        throw new Error("Search stream failed");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() ?? "";

        for (const chunk of chunks) {
          const lines = chunk.split("\n");
          let event = "message";
          let data = "";

          for (const line of lines) {
            if (line.startsWith("event:")) event = line.slice(6).trim();
            if (line.startsWith("data:")) data += line.slice(5).trim();
          }

          if (!data) continue;

          if (event === "progress") {
            onProgress(JSON.parse(data));
          } else if (event === "result") {
            onResult(JSON.parse(data));
          }
        }
      }
    })
    .catch((error) => {
      if (error.name !== "AbortError") {
        onError(error.message ?? "Unexpected error");
      }
    });

  return () => controller.abort();
}
