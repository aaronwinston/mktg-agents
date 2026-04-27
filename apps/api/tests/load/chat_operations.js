import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  stages: [
    { duration: '30s', target: 100 },  // Ramp up to 100 VUs
    { duration: '1m', target: 400 },   // Ramp up to 400 VUs
    { duration: '1m', target: 1000 },  // Ramp up to 1000 VUs
    { duration: '2m', target: 1000 },  // Hold at 1000 VUs
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(90)<500', 'p(95)<750', 'p(99)<1000'],
    'http_req_failed': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

function getTestToken() {
  return __ENV.TEST_TOKEN || 'test-token';
}

export default function() {
  const token = getTestToken();
  const sessionId = __ENV.SESSION_ID || 'test-session';
  const messageContent = `Message ${randomString(20)}`;

  // Create chat message
  let createMsgRes = http.post(`${BASE_URL}/api/chat/sessions/${sessionId}/messages`, {
    content: messageContent,
    role: 'user',
  }, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  check(createMsgRes, {
    'create message status is 200/201': (r) => r.status === 200 || r.status === 201,
    'create message response time < 600ms': (r) => r.timings.duration < 600,
  });

  sleep(0.05);

  // List messages
  let listMsgRes = http.get(`${BASE_URL}/api/chat/sessions/${sessionId}/messages`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  check(listMsgRes, {
    'list messages status is 200': (r) => r.status === 200,
    'list messages response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(0.05);

  // Get chat session
  let getSessionRes = http.get(`${BASE_URL}/api/chat/sessions/${sessionId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  check(getSessionRes, {
    'get session status is 200': (r) => r.status === 200,
    'get session response time < 400ms': (r) => r.timings.duration < 400,
  });

  sleep(0.1);
}
