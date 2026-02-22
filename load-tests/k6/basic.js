//   k6 run --summary-export=./results/k6-summary.json load-tests/k6/basic.js
// Step-load variant: use --env SCENARIO=ramp in options below (see comment).

import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";
const PRODUCT_IDS = [
  "OLJCESPC7Z",
  "66VCHSJNUP",
  "1YMWWN1N4O",
  "2ZYFJ3GM2N",
  "0PUK6V6EV0",
];

const scenario = __ENV.SCENARIO || "constant_rate";
export const options = {
  scenarios:
    scenario === "ramp"
      ? {
          step_load: {
            executor: "ramping-vus",
            startVUs: 0,
            stages: [
              { duration: "1m", target: 25 },
              { duration: "1m", target: 50 },
              { duration: "1m", target: 75 },
            ],
            startTime: "0s",
            gracefulRampDown: "30s",
            gracefulStop: "10s",
          },
        }
      : {
          constant_rate: {
            executor: "constant-arrival-rate",
            rate: 50,
            timeUnit: "1s",
            duration: "5m",
            preAllocatedVUs: 10,
            maxVUs: 50,
          },
        },
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<2000", "p(99)<5000"],
  },
};

export default function () {
  const productId = PRODUCT_IDS[Math.floor(Math.random() * PRODUCT_IDS.length)];
  const res = http.get(`${BASE_URL}/api/data/?contextKeys=telescopes`);
  check(res, { "status is 200": (r) => r.status === 200 });
  sleep(0.1);
}
