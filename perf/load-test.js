import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2s', target: 20 },
    { duration: '6s', target: 20 },
    { duration: '2s', target: 0 },
  ],
};

export default function () {
  const res = http.get('http://localhost:8000/quotes/today');
  check(res, {
    'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
  });
  sleep(0.1);
}
