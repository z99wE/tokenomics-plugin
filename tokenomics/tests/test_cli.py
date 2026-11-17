"""CLI tests — tests tokenomics/cli.py

Covers CLI command handlers, parser building, and return codes.
Uses a temp state path via StateManager constructor injection.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

# Ensure the package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenomics.cli import (
    build_parser,
    cmd_achievements,
    cmd_audit,
    cmd_budget,
    cmd_defaults,
    cmd_disable,
    cmd_domain,
    cmd_enable,
    cmd_estimate,
    cmd_ladder,
    cmd_learn,
    cmd_logo,
    cmd_project,
    cmd_record,
    cmd_review,
    cmd_status,
    main,
)
from tokenomics.state import StateManager


class TestCLIHandlers(unittest.TestCase):
    """Test individual CLI command handlers."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state_path = os.path.join(self.tmpdir, "state.json")
        self.lock_path = os.path.join(self.tmpdir, "state.lock")
        self.sm = StateManager(state_path=self.state_path)
        # Patch StateManager in the cli module so all CLI commands use our temp state
        self._state_patch = patch("tokenomics.cli.StateManager", return_value=self.sm)
        self._state_patch.start()

    def tearDown(self):
        self._state_patch.stop()

    def _namespace(self, **kwargs):
        return argparse.Namespace(**kwargs)

    def test_cmd_enable(self):
        self.sm.disable()
        result = cmd_enable(self._namespace())
        self.assertEqual(result, 0)
        self.assertTrue(self.sm.load()["enabled"])

    def test_cmd_disable(self):
        self.sm.enable()
        result = cmd_disable(self._namespace())
        self.assertEqual(result, 0)
        self.assertFalse(self.sm.load()["enabled"])

    def test_cmd_status(self):
        self.sm.enable()
        result = cmd_status(self._namespace())
        self.assertEqual(result, 0)

    def test_cmd_estimate(self):
        result = cmd_estimate(self._namespace(text="This is a test."))
        self.assertEqual(result, 0)

    def test_cmd_estimate_no_text(self):
        result = cmd_estimate(self._namespace(text=None))
        self.assertEqual(result, 1)

    def test_cmd_review(self):
        result = cmd_review(self._namespace(code="x = 1 + 2"))
        self.assertEqual(result, 0)

    def test_cmd_review_no_code(self):
        result = cmd_review(self._namespace(code=None))
        self.assertEqual(result, 1)

    def test_cmd_audit(self):
        self.sm.enable()
        result = cmd_audit(self._namespace())
        self.assertEqual(result, 0)

    def test_cmd_ladder(self):
        result = cmd_ladder(self._namespace())
        self.assertEqual(result, 0)

    def test_cmd_logo(self):
        result = cmd_logo(self._namespace())
        self.assertEqual(result, 0)

    def test_cmd_domain_never(self):
        result = cmd_domain(self._namespace(domain_action="never", domain_name="security"))
        self.assertEqual(result, 0)
        rules = self.sm.get_domain_rules()
        self.assertIn("security", rules.never_compress)

    def test_cmd_domain_always(self):
        result = cmd_domain(self._namespace(domain_action="always", domain_name="docs"))
        self.assertEqual(result, 0)
        rules = self.sm.get_domain_rules()
        self.assertIn("docs", rules.always_compress)

    def test_cmd_domain_preset(self):
        result = cmd_domain(self._namespace(domain_action="preset", domain_name="commit", preset_name="commit"))
        self.assertEqual(result, 0)
        self.assertEqual(self.sm.get_domain_preset("commit"), "commit")

    def test_cmd_domain_list(self):
        result = cmd_domain(self._namespace(domain_action="list", domain_name=None))
        self.assertEqual(result, 0)

    def test_cmd_achievements(self):
        self.sm.enable()
        result = cmd_achievements(self._namespace())
        self.assertEqual(result, 0)

    def test_cmd_budget_set(self):
        result = cmd_budget(self._namespace(budget_action="set", limit=5000))
        self.assertEqual(result, 0)
        self.assertEqual(self.sm.get_token_budget(), 5000)

    def test_cmd_budget_check(self):
        self.sm.set_token_budget(3000)
        result = cmd_budget(self._namespace(budget_action="check", limit=None))
        self.assertEqual(result, 0)

    def test_cmd_record(self):
        self.sm.set_token_budget(1000)
        result = cmd_record(self._namespace(tokens=500))
        self.assertEqual(result, 0)

    def test_cmd_project(self):
        result = cmd_project(self._namespace(type="web"))
        self.assertEqual(result, 0)
        self.assertEqual(self.sm.get_project_type(), "web")

    def test_cmd_learn(self):
        result = cmd_learn(self._namespace(enable=True))
        self.assertEqual(result, 0)
        self.assertTrue(self.sm.load()["auto_learn"])

    def test_cmd_defaults(self):
        result = cmd_defaults(self._namespace(enable=True))
        self.assertEqual(result, 0)
        self.assertTrue(self.sm.load()["smart_defaults"])


class TestCLIParser(unittest.TestCase):
    """Test argument parser construction."""

    def test_parser_has_all_subcommands(self):
        parser = build_parser()
        # The subparsers action itself
        subparser_action = None
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                subparser_action = action
                break
        self.assertIsNotNone(subparser_action)
        expected = {
            "enable", "disable", "status", "estimate", "review", "audit",
            "ladder", "logo", "domain", "achievements", "budget",
            "record", "project", "learn", "defaults",
        }
        actual = set(subparser_action.choices.keys())
        self.assertEqual(actual, expected)

    def test_main_no_command(self):
        result = main([])
        self.assertEqual(result, 1)

    def test_main_enable(self):
        result = main(["enable"])
        self.assertEqual(result, 0)

    def test_main_disable(self):
        result = main(["disable"])
        self.assertEqual(result, 0)

    def test_main_status(self):
        result = main(["status"])
        self.assertEqual(result, 0)

    def test_main_estimate(self):
        result = main(["estimate", "test text"])
        self.assertEqual(result, 0)

    def test_main_review(self):
        result = main(["review", "--code", "x = 1"])
        self.assertEqual(result, 0)

    def test_main_budget_set(self):
        result = main(["budget", "set", "5000"])
        self.assertEqual(result, 0)

    def test_main_budget_check(self):
        result = main(["budget", "check"])
        self.assertEqual(result, 0)

    def test_main_record(self):
        result = main(["record", "500"])
        self.assertEqual(result, 0)

    def test_main_project(self):
        result = main(["project", "web"])
        self.assertEqual(result, 0)

    def test_main_learn(self):
        result = main(["learn"])
        self.assertEqual(result, 0)

    def test_main_defaults(self):
        result = main(["defaults"])
        self.assertEqual(result, 0)

    def test_main_unknown_command(self):
        # argparse exits with SystemExit(2) for unknown subcommand
        with self.assertRaises(SystemExit) as ctx:
            main(["bogus"])
        self.assertNotEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
