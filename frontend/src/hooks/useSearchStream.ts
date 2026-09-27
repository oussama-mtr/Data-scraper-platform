import { useCallback, useState } from "react";
import { streamSearch } from "../services/api";
import type { ProgressEvent, SearchResult } from "../types";

export function useSearchStream() {
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startSearch = useCallback((query: string) => {
    setIsSearching(true);
    setProgress(null);
    setResult(null);
    setError(null);

    const cancel = streamSearch(
      query,
      (event) => setProgress(event),
      (searchResult) => {
        setResult(searchResult);
        setIsSearching(false);
      },
      (message) => {
        setError(message);
        setIsSearching(false);
      },
    );

    return cancel;
  }, []);

  const reset = useCallback(() => {
    setProgress(null);
    setResult(null);
    setError(null);
    setIsSearching(false);
  }, []);

  return { progress, isSearching, result, error, startSearch, reset };
}
