import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";
const USERNAME = __ENV.USERNAME || "user";
const PASSWORD = __ENV.PASSWORD || "password";
const HEADERS = {
  "Content-Type": "application/json",
  "x-forwarded-for": __ENV.FAKE_IP || "203.0.113.1",
};

const scenario = "constant_rate";
const rps = parseInt(__ENV.RPS || "50", 10);
const duration = __ENV.DURATION || "60s";
const sloP95Ms = parseInt(__ENV.SLO_P95_MS || "500", 10);
const sloErrorRate = parseFloat(__ENV.SLO_ERROR_RATE || "0.01");
const maxVUs = Math.min(1000, Math.max(rps + 200, 100));
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
            rate: rps,
            timeUnit: "1s",
            duration: duration,
            preAllocatedVUs: Math.min(maxVUs, rps + 120),
            maxVUs: maxVUs,
          },
        },
  thresholds: {
    http_req_failed: [`rate<${sloErrorRate}`],
    http_req_duration: [`p(95)<${sloP95Ms}`],
  },
};

export default function () {
  const res = http.post(
    `${BASE_URL}/api/user/login`,
    JSON.stringify({ name: USERNAME, password: PASSWORD }),
    { headers: HEADERS },
  );
  check(res, {
    "status is 200": (r) => r.status === 200,
    "has user name": (r) => {
      try {
        const b = r.json();
        return b && b.name !== undefined;
      } catch (e) {
        return false;
      }
    },
  });
  sleep(0.1);
}
