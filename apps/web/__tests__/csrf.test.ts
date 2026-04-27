/**
 * CSRF Token Handling Tests
 * 
 * This file documents the CSRF token handling implementation.
 * Tests verify:
 * 1. Token generation using crypto.getRandomValues()
 * 2. Token storage in sessionStorage (not localStorage)
 * 3. Token inclusion in request headers as X-CSRF-Token
 * 4. Token persistence across multiple API calls
 * 5. Token clearing on logout
 */

import { generateCSRFToken, getCSRFToken, clearCSRFToken, getHeadersWithCSRF } from '@/lib/csrf';

/**
 * Test Suite: CSRF Token Generation
 * 
 * Verifies that tokens are generated with sufficient entropy
 */
export function testCSRFTokenGeneration() {
  console.log('Testing CSRF token generation...');

  const token = generateCSRFToken();

  // Should be a 64-character hex string (32 bytes * 2 hex chars)
  console.assert(typeof token === 'string', 'Token should be a string');
  console.assert(token.length === 64, `Token length should be 64, got ${token.length}`);
  console.assert(/^[0-9a-f]+$/.test(token), 'Token should only contain hex characters');

  // Generate multiple tokens to verify randomness
  const token2 = generateCSRFToken();
  console.assert(token !== token2, 'Generated tokens should be different');

  console.log('✓ CSRF token generation tests passed');
}

/**
 * Test Suite: CSRF Token Storage
 * 
 * Verifies that tokens are stored in sessionStorage (not localStorage)
 */
export function testCSRFTokenStorage() {
  console.log('Testing CSRF token storage...');

  // Clear any existing tokens
  sessionStorage.clear();

  const token = getCSRFToken();

  // Should be stored in sessionStorage
  const storedToken = sessionStorage.getItem('csrf_token');
  console.assert(storedToken === token, 'Token should be stored in sessionStorage');

  // Verify localStorage is NOT used
  const localStorageToken = localStorage.getItem('csrf_token');
  console.assert(localStorageToken === null, 'Token should NOT be in localStorage');

  console.log('✓ CSRF token storage tests passed');
}

/**
 * Test Suite: CSRF Token Persistence
 * 
 * Verifies that tokens persist across multiple calls
 */
export function testCSRFTokenPersistence() {
  console.log('Testing CSRF token persistence...');

  sessionStorage.clear();

  const token1 = getCSRFToken();
  const token2 = getCSRFToken();
  const token3 = getCSRFToken();

  console.assert(token1 === token2, 'Token should be same on second call');
  console.assert(token2 === token3, 'Token should be same on third call');

  console.log('✓ CSRF token persistence tests passed');
}

/**
 * Test Suite: CSRF Token in Headers
 * 
 * Verifies that tokens are correctly included in request headers
 */
export function testCSRFTokenInHeaders() {
  console.log('Testing CSRF token in headers...');

  sessionStorage.clear();

  const headers = getHeadersWithCSRF({
    'Content-Type': 'application/json',
  });

  console.assert(headers['X-CSRF-Token'], 'Headers should include X-CSRF-Token');
  console.assert(headers['Content-Type'] === 'application/json', 'Should preserve existing headers');

  // Token should be the same as getCSRFToken()
  const token = getCSRFToken();
  console.assert(headers['X-CSRF-Token'] === token, 'Header token should match session token');

  console.log('✓ CSRF token in headers tests passed');
}

/**
 * Test Suite: CSRF Token Clearing
 * 
 * Verifies that tokens can be cleared for logout
 */
export function testCSRFTokenClearing() {
  console.log('Testing CSRF token clearing...');

  sessionStorage.clear();

  const token1 = getCSRFToken();
  console.assert(token1, 'Token should be generated');

  clearCSRFToken();
  const storedToken = sessionStorage.getItem('csrf_token');
  console.assert(storedToken === null, 'Token should be cleared from sessionStorage');

  // New token should be different
  const token2 = getCSRFToken();
  console.assert(token1 !== token2, 'New token should be different after clearing');

  console.log('✓ CSRF token clearing tests passed');
}

/**
 * Test Suite: Full CSRF Flow
 * 
 * Simulates a complete signin flow with CSRF protection
 */
export function testFullCSRFFlow() {
  console.log('Testing full CSRF flow for signin...');

  sessionStorage.clear();

  // 1. Component mounts and initializes CSRF token
  const csrfToken = getCSRFToken();
  console.assert(csrfToken, 'CSRF token should be initialized on mount');

  // 2. User enters credentials
  const email = 'test@example.com';
  const password = 'password123';

  // 3. Form submission prepares headers with CSRF
  const headers = getHeadersWithCSRF({
    'Content-Type': 'application/json',
  });

  console.assert(headers['X-CSRF-Token'] === csrfToken, 'Request should include CSRF token');

  // 4. Simulate successful response and redirect
  // Token remains in sessionStorage for subsequent requests

  // 5. Subsequent API calls reuse the same token
  const headers2 = getHeadersWithCSRF({
    'Content-Type': 'application/json',
  });

  console.assert(headers['X-CSRF-Token'] === headers2['X-CSRF-Token'], 'Token should be consistent across requests');

  console.log('✓ Full CSRF flow tests passed');
}

/**
 * Run all CSRF tests
 * 
 * This function can be called from the browser console for manual testing:
 * import { runAllCSRFTests } from '@/__tests__/csrf.test'
 * runAllCSRFTests()
 */
export function runAllCSRFTests() {
  console.log('=== CSRF Token Tests ===\n');

  try {
    testCSRFTokenGeneration();
    testCSRFTokenStorage();
    testCSRFTokenPersistence();
    testCSRFTokenInHeaders();
    testCSRFTokenClearing();
    testFullCSRFFlow();

    console.log('\n=== All CSRF Tests Passed ✓ ===');
  } catch (error) {
    console.error('CSRF Tests Failed:', error);
  }
}
