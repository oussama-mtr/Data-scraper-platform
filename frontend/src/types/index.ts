export type AppView =
  | "landing"
  | "chat"
  | "wizard"
  | "results"
  | "history"
  | "downloads"
  | "settings";

export interface Source {
  id: string;
  name: string;
  url: string;
  type: string;
  domain: string;
  keywords: string[];
}

export interface ProgressEvent {
  stage: string;
  message: string;
  progress: number;
}

export interface DownloadedFile {
  name: string;
  url: string;
  size_bytes: number;
  source_id: string;
  local_path?: string | null;
}

export interface SearchResult {
  id: string;
  query: string;
  summary: string;
  sources_consulted: Array<Pick<Source, "id" | "name" | "url" | "type">>;
  downloaded_files: DownloadedFile[];
  table_preview: Array<Record<string, unknown>>;
  excel_path?: string | null;
  status: string;
  created_at: string;
  messages: string[];
}

export interface HistoryItem {
  id: string;
  query: string;
  status: string;
  created_at: string;
  sources_count: number;
  files_count: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}
