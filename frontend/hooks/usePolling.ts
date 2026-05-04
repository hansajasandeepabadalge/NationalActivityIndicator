import { useState, useEffect, useCallback, useRef } from 'react';

interface UsePollingOptions {
  interval?: number; // milliseconds
  enabled?: boolean;
  onError?: (error: Error) => void;
}

interface UsePollingResult<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

/**
 * Hook for polling data at regular intervals
 * @param fetchFn - Async function that fetches the data
 * @param options - Polling configuration
 * @returns Polling state and control functions
 */
export function usePolling<T>(
  fetchFn: () => Promise<T>,
  options: UsePollingOptions = {}
): UsePollingResult<T> {
  const {
    interval = 30000, // Default 30 seconds
    enabled = true,
    onError
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchFnRef = useRef(fetchFn);
  const onErrorRef = useRef(onError);

  // Update refs when dependencies change
  useEffect(() => {
    fetchFnRef.current = fetchFn;
    onErrorRef.current = onError;
  }, [fetchFn, onError]);

  const fetch = useCallback(async () => {
    try {
      const result = await fetchFnRef.current();
      setData(result);
      setError(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      onErrorRef.current?.(error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refetch = useCallback(async () => {
    setIsLoading(true);
    await fetch();
  }, [fetch]);

  useEffect(() => {
    if (!enabled) {
      setIsLoading(false);
      return;
    }

    // Initial fetch
    fetch();

    // Set up polling interval
    const timer = setInterval(fetch, interval);

    return () => {
      clearInterval(timer);
    };
  }, [enabled, interval, fetch]);

  return { data, isLoading, error, refetch };
}
