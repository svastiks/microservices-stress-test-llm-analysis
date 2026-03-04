import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const USERNAME = __ENV.USERNAME || "stress_signup";
const PASSWORD = __ENV.PASSWORD || "test_signup";
const HEADERS = {
  "Content-Type": "application/json",
};

export const options = {
  scenarios: {
    signup: {
      executor: "constant-arrival-rate",
      rate: parseInt(__ENV.RPS || "100", 10),
      timeUnit: "1s",
      duration: __ENV.DURATION || "90s",
      preAllocatedVUs: parseInt(__ENV.maxVUs || "150", 10),
      maxVUs: parseInt(__ENV.maxVUs || "150", 10),
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<2000", "p(99)<5000"],
  },
};

export default function () {
  const res = http.post(
    `${BASE_URL}/signup`,
    JSON.stringify({ username: USERNAME, password: PASSWORD }),
    { headers: HEADERS },
  );
  check(res, {
    "status is 200": (r) => r.status === 200,
    "has hash": (r) => {
      if (r.status !== 200 || !r.body) return false;
      try {
        return r.json("password_hash") !== undefined;
      } catch (_) {
        return false;
      }
    },
  });
  sleep(0.1);
}

