"""LLM JSON fields must survive markdown fence wrappers."""
from __future__ import annotations

import unittest

import yaml

from analysis.results import (
    _normalize_llm_yaml_fields,
    _strip_markdown_yaml_fences,
)


class TestLlmYamlFenceStrip(unittest.TestCase):
    def test_strip_yaml_fence(self) -> None:
        raw = "```yaml\napiVersion: apps/v1\nkind: Deployment\n```"
        out = _strip_markdown_yaml_fences(raw)
        doc = yaml.safe_load(out)
        self.assertEqual(doc["kind"], "Deployment")

    def test_strip_plain_yaml_unchanged(self) -> None:
        raw = "apiVersion: apps/v1\nkind: Deployment"
        self.assertEqual(_strip_markdown_yaml_fences(raw), raw)

    def test_normalize_llm_yaml_fields(self) -> None:
        result = {
            "deployment_yaml_new": "```yaml\napiVersion: v1\nkind: Deployment\n```",
            "hpa_yaml_new": "",
            "report": "ok",
        }
        _normalize_llm_yaml_fields(result)
        self.assertTrue(result["deployment_yaml_new"].startswith("apiVersion:"))
        yaml.safe_load(result["deployment_yaml_new"])


if __name__ == "__main__":
    unittest.main()
