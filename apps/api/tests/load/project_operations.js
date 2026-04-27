import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  stages: [
    { duration: '30s', target: 50 },   // Ramp up to 50 VUs
    { duration: '1m', target: 200 },   // Ramp up to 200 VUs
    { duration: '1m', target: 500 },   // Ramp up to 500 VUs
    { duration: '2m', target: 500 },   // Hold at 500 VUs
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(90)<500', 'p(95)<750', 'p(99)<1000'],
    'http_req_failed': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Generate a valid JWT token for testing
function getTestToken() {
  // This would need to be generated with proper signing
  // For now, use a test token from env or generate one
  return __ENV.TEST_TOKEN || 'test-token';
}

export default function() {
  const token = getTestToken();
  const projectName = `Project ${randomString(10)}`;
  const projectDesc = `Test project for ${randomString(5)}`;

  // Create project
  let createRes = http.post(`${BASE_URL}/api/projects`, {
    name: projectName,
    description: projectDesc,
  }, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  check(createRes, {
    'create status is 200/201': (r) => r.status === 200 || r.status === 201,
    'create response time < 500ms': (r) => r.timings.duration < 500,
  });

  let projectId = '';
  if (createRes.status === 200 || createRes.status === 201) {
    try {
      projectId = createRes.json().id;
    } catch (e) {
      console.log('Could not parse project creation response:', e);
    }
  }

  sleep(0.05);

  // List projects
  let listRes = http.get(`${BASE_URL}/api/projects`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  check(listRes, {
    'list status is 200': (r) => r.status === 200,
    'list response time < 400ms': (r) => r.timings.duration < 400,
  });

  sleep(0.05);

  // Get project details if we have an ID
  if (projectId) {
    let getRes = http.get(`${BASE_URL}/api/projects/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    check(getRes, {
      'get status is 200': (r) => r.status === 200,
      'get response time < 300ms': (r) => r.timings.duration < 300,
    });

    sleep(0.05);

    // Update project
    let updateRes = http.put(`${BASE_URL}/api/projects/${projectId}`, {
      name: `Updated ${projectName}`,
      description: `Updated description`,
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    check(updateRes, {
      'update status is 200': (r) => r.status === 200,
      'update response time < 400ms': (r) => r.timings.duration < 400,
    });

    sleep(0.05);

    // Delete project
    let deleteRes = http.delete(`${BASE_URL}/api/projects/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    check(deleteRes, {
      'delete status is 200/204': (r) => r.status === 200 || r.status === 204,
      'delete response time < 300ms': (r) => r.timings.duration < 300,
    });
  }

  sleep(0.5);
}
