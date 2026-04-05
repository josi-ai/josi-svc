import type { ApiResponse } from '@/types';

/**
 * Extract the data field from an API response.
 * Handles both direct data and nested ResponseModel wrapper.
 */
export function extractData<T>(response: ApiResponse<T> | undefined | null): T | null {
  if (!response) return null;
  return response.data ?? null;
}

/**
 * Extract an array from an API response that may return either
 * a flat array or a nested object with the array inside.
 *
 * Example: astrologers endpoint returns { astrologers: [], total: 0 }
 * This extracts the array regardless of nesting.
 */
export function extractArray<T>(
  response: ApiResponse<unknown> | undefined | null,
  key?: string
): T[] {
  if (!response?.data) return [];
  const data = response.data;
  if (Array.isArray(data)) return data as T[];
  if (key && typeof data === 'object' && data !== null) {
    const nested = (data as Record<string, unknown>)[key];
    if (Array.isArray(nested)) return nested as T[];
  }
  return [];
}

/**
 * Extract transit data -- handles the specific shape where
 * transits are nested under major_transits key.
 */
export function extractTransits(response: ApiResponse<unknown> | undefined | null) {
  return extractArray(response, 'major_transits');
}

/**
 * Extract consultations from the nested response shape.
 */
export function extractConsultations(response: ApiResponse<unknown> | undefined | null) {
  return extractArray(response, 'consultations');
}

/**
 * Extract astrologers from the nested response shape.
 */
export function extractAstrologers(response: ApiResponse<unknown> | undefined | null) {
  return extractArray(response, 'astrologers');
}
