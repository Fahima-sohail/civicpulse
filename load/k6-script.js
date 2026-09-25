import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '90s', target: 80 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<2000'],
  },
};

const baseUrl = __ENV.BASE_URL || 'http://civicpulse.local';

export default function () {
  // GET avoids the intentional POST rate limiter while concentrating load on the backend.
  const response = http.get(`${baseUrl}/api/complaints?page=1&page_size=20`);

  check(response, {
    'complaint list returned': (result) => result.status === 200,
  });
}
