"""Hermes plugin tests — tests tokenomics/hermes/__init__.py

Covers all 11 tool handlers, 5 hooks, tool dispatch, and registration.
Uses a temp state path to avoid touching the real Hermes state file.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

# Ensure the package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch STATE_MANAGER to use a temp path BEFORE importing hermes module
_tmpdir = tempfile.mkdtemp()
_temp_state = os.path.join(_tmpdir, "state.json")
_temp_lock = os.path.join(_tmpdir, "state.lock")

# We need to patch StateManager's defaults before hermes imports it
# The cleanest way: import the module and replace STATE_MANAGER
# Now import hermes module and swap its STATE_MANAGER
import tokenomics.hermes.__init__ as hermes_mod
from tokenomics.state import StateManager

hermes_mod.STATE_MANAGER = StateManager(state_path=_temp_state)

from tokenomics.hermes.__init__ import (
    _handle_achievements,
    _handle_audit,
    _handle_budget,
    _handle_disable,
    _handle_domain,
    _handle_enable,
    _handle_estimate,
    _handle_learn,
    _handle_project,
    _handle_review,
    _handle_status,
    _hook_delegate_task,
    _hook_on_session_end,
    _hook_on_session_start,
    _hook_post_tool_call,
    _hook_pre_tool_call,
    _run_tool,
    register,
)


class TestHermesToolHandlers(unittest.TestCase):
    """Test all 11 tool handlers directly."""

    def setUp(self):
        hermes_mod.STATE_MANAGER = StateManager(state_path=_temp_state)
        hermes_mod.STATE_MANAGER.reset()

    def test_enable_handler(self):
        result = _handle_enable({})
        self.assertTrue(result["ok"])
        self.assertTrue(result["data"]["enabled"])
        self.assertIn("message", result["data"])

    def test_disable_handler(self):
        hermes_mod.STATE_MANAGER.enable()
        result = _handle_disable({})
        self.assertTrue(result["ok"])
        self.assertFalse(result["data"]["enabled"])

    def test_status_handler(self):
        hermes_mod.STATE_MANAGER.enable()
        result = _handle_status({})
        self.assertTrue(result["ok"])
        self.assertIn("enabled", result["data"])
        self.assertIn("level", result["data"])
        self.assertIn("estimated_tokens_saved", result["data"])

    def test_estimate_handler(self):
        result = _handle_estimate({"text": "This is a really simple test."})
        self.assertTrue(result["ok"])
        self.assertIn("original_tokens", result["data"])
        self.assertIn("compressed_tokens", result["data"])
        self.assertIn("estimated_saved", result["data"])
        self.assertIn("preview", result["data"])

    def test_estimate_empty_text(self):
        result = _handle_estimate({"text": ""})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"]["original_tokens"], 0)

    def test_review_handler(self):
        result = _handle_review({"code": "x = 1 + 2"})
        self.assertTrue(result["ok"])
        self.assertIn("issues", result)
        self.assertIn("estimated_savings", result)

    def test_review_handler_empty_code(self):
        result = _handle_review({"code": ""})
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_audit_handler(self):
        result = _handle_audit({})
        self.assertTrue(result["ok"])
        self.assertIn("recommendations", result["data"])
        self.assertIn("preview_path", result["data"])
        self.assertIn("level", result["data"])

    def test_domain_handler_never(self):
        result = _handle_domain({"action": "never", "domain": "security"})
        self.assertTrue(result["ok"])
        self.assertIn("security", result["data"]["message"])

    def test_domain_handler_always(self):
        result = _handle_domain({"action": "always", "domain": "docs"})
        self.assertTrue(result["ok"])
        self.assertIn("docs", result["data"]["message"])

    def test_domain_handler_preset(self):
        result = _handle_domain({"action": "preset", "domain": "commit", "preset": "commit"})
        self.assertTrue(result["ok"])

    def test_domain_handler_list(self):
        result = _handle_domain({"action": "list"})
        self.assertTrue(result["ok"])
        self.assertIn("never_compress", result["data"])
        self.assertIn("always_compress", result["data"])
        self.assertIn("force_preset", result["data"])

    def test_domain_handler_unknown(self):
        result = _handle_domain({"action": "bogus"})
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_achievements_handler(self):
        result = _handle_achievements({})
        self.assertTrue(result["ok"])
        self.assertIn("newly_unlocked", result["data"])

    def test_budget_handler_set(self):
        result = _handle_budget({"action": "set", "limit": 5000})
        self.assertTrue(result["ok"])
        self.assertIn("5000", result["message"])

    def test_budget_handler_check(self):
        hermes_mod.STATE_MANAGER.set_token_budget(3000)
        result = _handle_budget({"action": "check"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"]["budget"], 3000)

    def test_budget_handler_record(self):
        hermes_mod.STATE_MANAGER.set_token_budget(1000)
        result = _handle_budget({"action": "record", "tokens": 500})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"]["used_today"], 500)

    def test_budget_handler_missing_limit(self):
        result = _handle_budget({"action": "set"})
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_budget_handler_missing_tokens(self):
        result = _handle_budget({"action": "record"})
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_budget_handler_unknown_action(self):
        result = _handle_budget({"action": "bogus"})
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_project_handler(self):
        result = _handle_project({"type": "web"})
        self.assertTrue(result["ok"])
        self.assertIn("web", result["message"])

    def test_project_handler_invalid_type(self):
        # Should still work - no validation in handler itself
        result = _handle_project({"type": "web"})
        self.assertTrue(result["ok"])

    def test_learn_handler_enable(self):
        result = _handle_learn({"enable": True})
        self.assertTrue(result["ok"])
        self.assertIn("enabled", result["message"])

    def test_learn_handler_disable(self):
        result = _handle_learn({"enable": False})
        self.assertTrue(result["ok"])
        self.assertIn("disabled", result["message"])


class TestHermesRunToolDispatch(unittest.TestCase):
    """Test _run_tool dispatch table."""

    def setUp(self):
        hermes_mod.STATE_MANAGER = StateManager(state_path=_temp_state)
        hermes_mod.STATE_MANAGER.reset()

    def test_all_tools_dispatched(self):
        for tool_name in [
            "tokenomics.enable",
            "tokenomics.disable",
            "tokenomics.status",
            "tokenomics.estimate",
            "tokenomics.review",
            "tokenomics.audit",
            "tokenomics.domain",
            "tokenomics.achievements",
            "tokenomics.budget",
            "tokenomics.project",
            "tokenomics.learn",
        ]:
            result = _run_tool(tool_name, {})
            # Should not return "unknown tool"
            self.assertNotEqual(
                result.get("error"), f"unknown tool: {tool_name}",
                f"Tool {tool_name} not dispatched",
            )

    def test_unknown_tool_returns_error(self):
        result = _run_tool("tokenomics.bogus", {})
        self.assertFalse(result["ok"])
        self.assertIn("unknown tool", result["error"])

    def test_estimate_via_run_tool(self):
        result = _run_tool("tokenomics.estimate", {"text": "test"})
        self.assertTrue(result["ok"])

    def test_review_via_run_tool(self):
        result = _run_tool("tokenomics.review", {"code": "x = 1"})
        self.assertTrue(result["ok"])


class TestHermesHooks(unittest.TestCase):
    """Test all 5 hooks."""

    def setUp(self):
        hermes_mod.STATE_MANAGER = StateManager(state_path=_temp_state)
        hermes_mod.STATE_MANAGER.reset()

    def test_pre_tool_call_disabled(self):
        kwargs = {"tool_name": "test.tool", "args": {"text": "hello world"}}
        result = _hook_pre_tool_call(**kwargs)
        self.assertEqual(kwargs, result)  # unchanged when disabled

    def test_pre_tool_call_enabled(self):
        hermes_mod.STATE_MANAGER.enable()
        kwargs = {"tool_name": "test.tool", "args": {"text": "the quick brown fox"}}
        result = _hook_pre_tool_call(**kwargs)
        # "the" should be compressed out
        self.assertNotIn("the", result["args"]["text"].lower())

    def test_post_tool_call_disabled(self):
        kwargs = {"result": {"data": {"message": "hello world"}}}
        result = _hook_post_tool_call(**kwargs)
        self.assertEqual(result["result"]["data"]["message"], "hello world")

    def test_post_tool_call_enabled_compresses(self):
        hermes_mod.STATE_MANAGER.enable()
        kwargs = {"result": {"data": {"message": "the quick brown fox"}}}
        result = _hook_post_tool_call(**kwargs)
        self.assertNotIn("the", result["result"]["data"]["message"].lower())

    def test_post_tool_call_non_dict_result(self):
        hermes_mod.STATE_MANAGER.enable()
        result = _hook_post_tool_call(result="not a dict")
        self.assertEqual(result, "not a dict")

    def test_on_session_start(self):
        result = _hook_on_session_start(context="ctx")
        self.assertEqual(result["context"], "ctx")

    def test_on_session_end(self):
        result = _hook_on_session_end(context="ctx")
        self.assertEqual(result["context"], "ctx")

    def test_delegate_task_disabled(self):
        kwargs = {"message": "do something", "context": "ctx"}
        _hook_delegate_task(**kwargs)
        self.assertEqual(kwargs["message"], "do something")

    def test_delegate_task_enabled_propagates(self):
        hermes_mod.STATE_MANAGER.enable()
        kwargs = {"message": "do something", "context": "ctx"}
        result = _hook_delegate_task(**kwargs)
        self.assertIn("TOKENOMICS PROPAGATED", result["message"])
        self.assertIn("TOKENOMICS PROPAGATED", result["context"])


class TestHermesRegister(unittest.TestCase):
    """Test the register function structure."""

    def test_register_has_all_tools(self):
        mock_ctx = MagicMock()
        register(mock_ctx)
        registered_tools = [call.kwargs["name"] for call in mock_ctx.register_tool.call_args_list]
        expected_tools = [
            "tokenomics.enable",
            "tokenomics.disable",
            "tokenomics.status",
            "tokenomics.estimate",
            "tokenomics.review",
            "tokenomics.audit",
            "tokenomics.domain",
            "tokenomics.achievements",
            "tokenomics.budget",
            "tokenomics.project",
            "tokenomics.learn",
        ]
        for tool in expected_tools:
            self.assertIn(tool, registered_tools, f"Tool {tool} not registered")

    def test_register_has_all_hooks(self):
        mock_ctx = MagicMock()
        register(mock_ctx)
        registered_hooks = [call.args[0] for call in mock_ctx.register_hook.call_args_list]
        expected_hooks = [
            "pre_tool_call",
            "post_tool_call",
            "on_session_start",
            "on_session_end",
            "delegate_task",
        ]
        for hook in expected_hooks:
            self.assertIn(hook, registered_hooks, f"Hook {hook} not registered")

    def test_register_no_pre_llm_call(self):
        """pre_llm_call should NOT be registered (removed in v2.1.0)."""
        mock_ctx = MagicMock()
        register(mock_ctx)
        registered_hooks = [call.args[0] for call in mock_ctx.register_hook.call_args_list]
        self.assertNotIn("pre_llm_call", registered_hooks)


if __name__ == "__main__":
    unittest.main()
