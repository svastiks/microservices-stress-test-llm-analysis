import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = "http://localhost:8080";
const HEADERS = {
  baggage: "session.id=test,synthetic_request=true",
};

const scenario = "constant_rate";
export const options = {
  scenarios:
    scenario === "ramp"
      ? {
          step_load: {
            executor: "ramping-vus",
            startVUs: 0,
            stages: [
              { duration: "1m", target: 10 },
              { duration: "1m", target: 20 },
              { duration: "1m", target: 30 },
            ],
            startTime: "0s",
            gracefulRampDown: "30s",
            gracefulStop: "10s",
          },
        }
      : {
          constant_rate: {
            executor: "constant-arrival-rate",
            rate: 40,
            timeUnit: "1s",
            duration: "30s",
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
  const res = http.get(`${BASE_URL}/api/data/?contextKeys=telescopes`, {
    headers: HEADERS,
  });
  check(res, { "status is 200": (r) => r.status === 200 });
  sleep(0.1);
}
