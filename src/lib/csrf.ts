/**
 * CSRF Token Management
 * Generates and manages CSRF tokens for protecting against Cross-Site Request Forgery attacks
 */

const CSRF_TOKEN_KEY = 'csrf_token';
const CSRF_HEADER_NAME = 'X-CSRF-Token';

/**
 * Generate a CSRF token using crypto.getRandomValues
 */
export function generateCSRFToken(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, (byte) => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * Get or create a CSRF token (stored in sessionStorage)
 */
export function getCSRFToken(): string {
  if (typeof window === 'undefined') {
    return '';
  }

  let token = sessionStorage.getItem(CSRF_TOKEN_KEY);

  if (!token) {
    token = generateCSRFToken();
    sessionStorage.setItem(CSRF_TOKEN_KEY, token);
  }

  return token;
}

/**
 * Clear the CSRF token (useful on logout)
 */
export function clearCSRFToken(): void {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(CSRF_TOKEN_KEY);
  }
}

/**
 * Get headers with CSRF token for state-changing requests
 */
export function getHeadersWithCSRF(
  headers: Record<string, string> = {}
): Record<string, string> {
  const csrfToken = getCSRFToken();
  return {
    ...headers,
    [CSRF_HEADER_NAME]: csrfToken,
  };
}
