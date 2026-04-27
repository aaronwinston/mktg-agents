import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 VUs
    { duration: '1m', target: 100 },   // Ramp up to 100 VUs
    { duration: '2m', target: 100 },   // Hold at 100 VUs
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(90)<600', 'p(95)<800', 'p(99)<1200'],
    'http_req_failed': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

function getTestToken() {
  return __ENV.TEST_TOKEN || 'test-token';
}

export default function() {
  const token = getTestToken();

  // Parallel requests to multiple dashboard endpoints
  let requests = {
    'dashboard': http.get(`${BASE_URL}/api/dashboard`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }),
    'projects': http.get(`${BASE_URL}/api/projects`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }),
    'recent_chats': http.get(`${BASE_URL}/api/chat/sessions`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }),
    'settings': http.get(`${BASE_URL}/api/settings`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }),
    'usage': http.get(`${BASE_URL}/api/usage`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }),
  };

  // Check all requests
  check(requests.dashboard, {
    'dashboard status is 200': (r) => r.status === 200,
    'dashboard response time < 600ms': (r) => r.timings.duration < 600,
  });

  check(requests.projects, {
    'projects status is 200': (r) => r.status === 200,
    'projects response time < 500ms': (r) => r.timings.duration < 500,
  });

  check(requests.recent_chats, {
    'recent_chats status is 200': (r) => r.status === 200,
    'recent_chats response time < 500ms': (r) => r.timings.duration < 500,
  });

  check(requests.settings, {
    'settings status is 200': (r) => r.status === 200,
    'settings response time < 400ms': (r) => r.timings.duration < 400,
  });

  check(requests.usage, {
    'usage status is 200': (r) => r.status === 200,
    'usage response time < 400ms': (r) => r.timings.duration < 400,
  });

  sleep(1);
}
