/**
 * Client-side query result cache with TTL (time-to-live)
 * Reduces redundant API calls and speeds up page loads
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttlSeconds: number;
}

class QueryCache {
  private cache: Map<string, CacheEntry<unknown>> = new Map();

  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined;
    if (!entry) return null;

    const now = Date.now();
    const age = (now - entry.timestamp) / 1000;

    if (age > entry.ttlSeconds) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  set<T>(key: string, data: T, ttlSeconds: number = 300): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttlSeconds,
    });
  }

  clear(key?: string): void {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }
}

export const queryCache = new QueryCache();

/**
 * Wrapper for API calls with automatic caching
 * Usage: await cachedFetch('/api/briefing', getBriefing, 300)
 */
export async function cachedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttlSeconds: number = 300
): Promise<T> {
  // Check cache first
  const cached = queryCache.get<T>(key);
  if (cached) {
    return cached;
  }

  // Fetch from API
  const data = await fetcher();

  // Cache the result
  queryCache.set(key, data, ttlSeconds);

  return data;
}
