import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { AppView, ChatMessage, SearchResult } from "../types";

interface AppState {
  view: AppView;
  setView: (view: AppView) => void;
  messages: ChatMessage[];
  addMessage: (message: Omit<ChatMessage, "id" | "timestamp">) => void;
  clearMessages: () => void;
  activeResult: SearchResult | null;
  setActiveResult: (result: SearchResult | null) => void;
}

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [view, setView] = useState<AppView>("landing");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeResult, setActiveResult] = useState<SearchResult | null>(null);

  const value = useMemo<AppState>(
    () => ({
      view,
      setView,
      messages,
      addMessage: (message) =>
        setMessages((current) => [
          ...current,
          {
            ...message,
            id: crypto.randomUUID(),
            timestamp: new Date().toISOString(),
          },
        ]),
      clearMessages: () => setMessages([]),
      activeResult,
      setActiveResult,
    }),
    [view, messages, activeResult],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppState() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppState must be used within AppProvider");
  }
  return context;
}
