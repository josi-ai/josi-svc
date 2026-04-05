import type { ApiResponse } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let getSessionToken: (() => Promise<string | null>) | null = null;
let authReadyPromise: Promise<void> | null = null;
let resolveAuthReady: (() => void) | null = null;

// Create a promise that resolves when auth is ready
function resetAuthReady() {
  authReadyPromise = new Promise((resolve) => {
    resolveAuthReady = resolve;
  });
}
resetAuthReady();

export function setTokenGetter(getter: () => string | undefined) {
  getSessionToken = async () => getter() ?? null;
}

export function setAsyncTokenGetter(getter: () => Promise<string | null>) {
  getSessionToken = getter;
}

/** Call this once Clerk is loaded and the user is signed in */
export function signalAuthReady() {
  resolveAuthReady?.();
}

/** Call this when the user signs out or auth state resets */
export function signalAuthReset() {
  resetAuthReady();
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  // Wait for auth to be ready before making any authenticated request
  // Times out after 5s to avoid hanging forever if auth never resolves
  if (authReadyPromise) {
    await Promise.race([
      authReadyPromise,
      new Promise((resolve) => setTimeout(resolve, 5000)),
    ]);
  }

  const token = await getSessionToken?.();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // Session expired — redirect to login instead of showing a broken page.
    // Only redirect if we actually sent a token (stale session). If no token
    // was available yet (auth still loading), the caller should handle the
    // error gracefully rather than triggering a redirect loop.
    if (response.status === 401 && typeof window !== 'undefined') {
      const path = window.location.pathname;
      const isPublicRoute = path === '/' || path.startsWith('/auth/') || path === '/pricing';
      if (!isPublicRoute && token) {
        window.location.href = '/auth/login';
        // Return a never-resolving promise so the redirect completes
        return new Promise(() => {});
      }
    }

    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.detail || error.message || 'Request failed');
  }

  // Handle 204 No Content (e.g., DELETE responses)
  if (response.status === 204) {
    return { success: true, message: 'OK', data: null as T };
  }

  const json = await response.json();

  // Validate response has expected wrapper shape
  if (typeof json !== 'object' || json === null) {
    throw new Error(`Invalid API response from ${endpoint}`);
  }

  return json as ApiResponse<T>;
}

export const apiClient = {
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, data?: any) =>
    request<T>(endpoint, { method: 'POST', body: data ? JSON.stringify(data) : undefined }),
  put: <T>(endpoint: string, data: any) =>
    request<T>(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: 'DELETE' }),
};
