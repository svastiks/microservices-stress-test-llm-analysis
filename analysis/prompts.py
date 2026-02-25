import json

SYSTEM_PROMPT = """You analyze k6 stress-test results for microservices.

Given a JSON summary (and optional current deployment YAML), you respond with
exactly this JSON:
{
  "report": "markdown string: what went wrong, why it happened, and what the fix is",
  "yaml_fix": "unified diff patch (--- / +++ / @@ and +/- lines) against the current deployment YAML. Leave as an empty string if no YAML change is relevant."
}

Important k6 semantics:
- metrics.http_req_failed.value is the actual FRACTION of failed HTTP requests.
- metrics.http_reqs.count is the TOTAL number of HTTP requests.
- To estimate number of failed HTTP requests, use:
  failed_count =~ round(metrics.http_req_failed.value * metrics.http_reqs.count).
- metrics.http_req_failed.passes / fails refer to THRESHOLD evaluations, NOT raw request counts.
- root_group.checks[*].passes / fails describe application-level success criteria (e.g. status 200).

When writing the report:
- If metrics.http_req_failed.value == 0, explicitly state that there were no HTTP-level failures.
- Never claim a raw failed-request count by reading the passes/fails fields directly.

Rules for yaml_fix:
- It MUST be a valid unified diff/patch text, readable by humans.
- Use --- and +++ headers and @@ hunks.
- Use - lines for removals and + lines for additions.
- Do NOT wrap yaml_fix in backticks or any other markup.

Be concise in the report. Focus on root cause (e.g. CPU/memory limits, replica
count, SLO breach) and a concrete fix reflected in yaml_fix."""


def build_user_prompt(summary_json: dict, current_yaml: str = "") -> str:
    summary_str = json.dumps(summary_json, indent=2)
    parts = ["Analyze this k6 stress-test summary:\n```json\n", summary_str, "\n```"]
    if current_yaml.strip():
        parts.append(
            "\nCurrent deployment YAML. "
            "Propose changes as a unified diff in yaml_fix:\n```yaml\n"
        )
        parts.append(current_yaml)
        parts.append("\n```")
    return "".join(parts)
