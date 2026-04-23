import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const USERNAME = __ENV.USERNAME || "stress";
const PASSWORD = __ENV.PASSWORD || "test";
const HEADERS = {
  "Content-Type": "application/json",
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
            rate: 450,
            timeUnit: "1s",
            duration: "60s",
            preAllocatedVUs: 450,
            maxVUs: 500,
          },
        },
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<400", "p(99)<800"],
  },
};

export default function () {
  const res = http.post(
    `${BASE_URL}/login`,
    JSON.stringify({ username: USERNAME, password: PASSWORD }),
    { headers: HEADERS },
  );
  check(res, {
    "status is 200": (r) => r.status === 200,
    "has token": (r) => r.json("token") !== undefined,
  });
  sleep(0.1);
}
