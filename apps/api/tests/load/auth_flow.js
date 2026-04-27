import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up to 10 VUs
    { duration: '1m', target: 50 },    // Ramp up to 50 VUs
    { duration: '1m', target: 100 },   // Ramp up to 100 VUs
    { duration: '2m', target: 100 },   // Hold at 100 VUs
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(90)<500', 'p(95)<750', 'p(99)<1000'],
    'http_req_failed': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function() {
  // Test signup/signin flow
  const email = `test${randomString(10)}@example.com`;
  const password = randomString(12);

  // Signup attempt
  let signupRes = http.post(`${BASE_URL}/api/auth/signup`, {
    email: email,
    password: password,
    full_name: 'Test User',
  }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });

  check(signupRes, {
    'signup status is 200/201': (r) => r.status === 200 || r.status === 201,
    'signup response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(0.1);

  // If signup successful, extract token
  let token = '';
  if (signupRes.status === 200 || signupRes.status === 201) {
    try {
      let body = signupRes.json();
      token = body.access_token || body.token;
    } catch (e) {
      console.log('Could not parse signup response:', e);
    }
  }

  // Login attempt
  let loginRes = http.post(`${BASE_URL}/api/auth/login`, {
    email: email,
    password: password,
  }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });

  check(loginRes, {
    'login status is 200': (r) => r.status === 200,
    'login response time < 400ms': (r) => r.timings.duration < 400,
    'login returns token': (r) => {
      try {
        return r.json().access_token || r.json().token;
      } catch {
        return false;
      }
    },
  });

  sleep(0.1);

  // Get profile with token (if we have one)
  if (loginRes.status === 200) {
    try {
      let body = loginRes.json();
      token = body.access_token || body.token;
      
      if (token) {
        let profileRes = http.get(`${BASE_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        check(profileRes, {
          'profile status is 200': (r) => r.status === 200,
          'profile response time < 300ms': (r) => r.timings.duration < 300,
        });
      }
    } catch (e) {
      console.log('Error in profile check:', e);
    }
  }

  sleep(1);
}
