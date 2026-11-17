"""Tokenomics test suite — stdlib-only, no pip dependencies.

Run with:  python -m pytest tokenomics/tests/  -v
           or: python -m unittest tokenomics.tests.test_core -v
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

# Ensure the package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenomics.core import (
    ACHIEVEMENTS,
    DomainPreset,
    DomainRules,
    Gamification,
    LearnedCompression,
    LearnedPattern,
    compress_prose,
    estimate_tokens,
    get_preset,
    is_safety_critical,
    ponytail_ladder,
    ponytail_rewrite,
    review_code,
)
from tokenomics.state import StateManager


# ---------------------------------------------------------------------------
# Core tests
# ---------------------------------------------------------------------------

class TestEstimateTokens(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(estimate_tokens(""), 0)

    def test_short_text(self):
        self.assertEqual(estimate_tokens("hi"), 1)  # 2 chars // 4 = 0 -> max(1, 0) = 1

    def test_known_length(self):
        # "hello world" = 11 chars, fallback = 11//4 = 2
        self.assertEqual(estimate_tokens("hello world"), 2)

    def test_none_is_zero(self):
        self.assertEqual(estimate_tokens(None), 0)


class TestGetPreset(unittest.TestCase):
    def test_standard_preset(self):
        p = get_preset("standard")
        self.assertIsInstance(p, DomainPreset)
        self.assertTrue(p.drop_articles)
        self.assertTrue(p.drop_filler)

    def test_unknown_preset_falls_back_to_standard(self):
        p = get_preset("does_not_exist")
        self.assertEqual(p.name, "standard")

    def test_commit_preset_more_aggressive(self):
        commit = get_preset("commit")
        standard = get_preset("standard")
        self.assertLess(commit.max_compression_ratio, standard.max_compression_ratio)


class TestCompressProse(unittest.TestCase):
    def test_empty_string_returns_empty(self):
        self.assertEqual(compress_prose(""), "")

    def test_removes_articles(self):
        result = compress_prose("the cat sat on a mat")
        self.assertNotIn("the", result.lower())
        self.assertNotIn("a ", result.lower())

    def test_removes_filler(self):
        result = compress_prose("this is really just basically simple")
        self.assertNotIn("really", result.lower())
        self.assertNotIn("basically", result.lower())

    def test_removes_pleasantries(self):
        result = compress_prose("sure, certainly, happy to help")
        self.assertNotIn("sure", result.lower())
        self.assertNotIn("certainly", result.lower())

    def test_removes_hedging(self):
        result = compress_prose("maybe I think it seems likely")
        self.assertNotIn("maybe", result.lower())
        self.assertNotIn("I think", result)

    def test_protects_code_blocks(self):
        text = "Here is code: ```python\nprint('hello')\n``` and some prose."
        result = compress_prose(text)
        self.assertIn("print('hello')", result)
        self.assertIn("```", result)

    def test_protects_inline_code(self):
        text = "Use `os.path.join` for paths."
        result = compress_prose(text)
        self.assertIn("os.path.join", result)

    def test_domain_never_compress(self):
        rules = DomainRules(never_compress={"security"})
        result = compress_prose("the API key is secret", domain="security", domain_rules=rules)
        self.assertEqual(result, "the API key is secret")  # unchanged

    def test_domain_always_compress(self):
        rules = DomainRules(always_compress={"docs"})
        result = compress_prose("the quick brown fox", domain="docs", domain_rules=rules)
        self.assertNotIn("the", result.lower())

    def test_force_preset(self):
        rules = DomainRules(force_preset={"commit": "commit"})
        result = compress_prose("fix the bug in the login function please", domain="commit", domain_rules=rules)
        # commit preset strips conjunctions and has max_compression_ratio 0.4
        self.assertNotIn("the", result.lower())

    def test_learned_revert_blocks_compression(self):
        learned = LearnedCompression()
        learned.record("domain:security", reverted=True)
        learned.record("domain:security", reverted=True)
        learned.record("domain:security", reverted=False)
        # 2 reverts / 3 total = 0.67 revert rate > 0.5, so should NOT compress
        self.assertFalse(learned.should_compress("domain:security"))

    def test_learned_accept_allows_compression(self):
        learned = LearnedCompression()
        learned.record("domain:docs", reverted=False)
        learned.record("domain:docs", reverted=False)
        self.assertTrue(learned.should_compress("domain:docs"))


class TestIsSafetyCritical(unittest.TestCase):
    def test_detects_auth_patterns(self):
        self.assertTrue(is_safety_critical("api_key = '12345'"))
        self.assertTrue(is_safety_critical("password = 'secret'"))
        self.assertTrue(is_safety_critical("token = 'abc'"))

    def test_detects_crypto_patterns(self):
        self.assertTrue(is_safety_critical("encrypt(data, key)"))
        self.assertTrue(is_safety_critical("hmac.sign(message)"))

    def test_detects_sql_patterns(self):
        self.assertTrue(is_safety_critical("SELECT * FROM users"))
        self.assertTrue(is_safety_critical("DROP TABLE users"))

    def test_detects_os_subprocess(self):
        self.assertTrue(is_safety_critical("os.system('rm -rf /')"))
        self.assertTrue(is_safety_critical("subprocess.run(cmd)"))

    def test_safe_code_passes(self):
        self.assertFalse(is_safety_critical("x = 1 + 2"))
        self.assertFalse(is_safety_critical("def hello(): return 'world'"))


class TestPonytailRewrite(unittest.TestCase):
    def test_none_code_returns_error(self):
        result = ponytail_rewrite("")
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_safety_critical_code_skipped(self):
        code = "api_key = 'sk-1234567890'\npassword = 'secret'"
        result = ponytail_rewrite(code, safe=True)
        self.assertTrue(result["ok"])
        self.assertFalse(result["safe"])
        self.assertIn("warnings", result)
        self.assertTrue(len(result["warnings"]) > 0)
        self.assertEqual(result["rewritten"], code)  # unchanged

    def test_removes_unused_imports(self):
        code = "import os\nimport json\nx = 1 + 2\n"
        result = ponytail_rewrite(code, safe=False)
        self.assertTrue(result["ok"])
        self.assertTrue(result["safe"])
        self.assertNotIn("import os", result["rewritten"])
        self.assertNotIn("import json", result["rewritten"])

    def test_applies_replacements(self):
        code = "if x == True:\n    pass\nif y == False:\n    pass\n"
        result = ponytail_rewrite(code, safe=False)
        self.assertTrue(result["ok"])
        self.assertIn("if x:", result["rewritten"])
        self.assertIn("if not y:", result["rewritten"])

    def test_removes_redundant_comments(self):
        code = "x = 1\n# this is a comment\ny = 2\n# TODO: fix this\n"
        result = ponytail_rewrite(code, safe=False)
        self.assertNotIn("this is a comment", result["rewritten"])
        self.assertIn("TODO: fix this", result["rewritten"])  # TODO preserved

    def test_returns_token_savings(self):
        code = "x = 1 + 1\n" * 20
        result = ponytail_rewrite(code, safe=False)
        self.assertGreaterEqual(result["estimated_savings"], 0)
        self.assertIn("original_tokens", result)
        self.assertIn("rewritten_tokens", result)


class TestPonytailLadder(unittest.TestCase):
    def test_returns_ladder_text(self):
        text = ponytail_ladder()
        self.assertIn("YAGNI", text)
        self.assertIn("stdlib", text.lower())
        self.assertIn("Does this need to exist?", text)
        self.assertIn("Never cut validation", text)


class TestReviewCode(unittest.TestCase):
    def test_empty_code_returns_error(self):
        result = review_code("")
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_none_code_returns_error(self):
        result = review_code(None)
        self.assertFalse(result["ok"])

    def test_short_clean_code_no_issues(self):
        code = "x = 1 + 2\nprint(x)"
        result = review_code(code)
        self.assertTrue(result["ok"])
        self.assertEqual(result["issues"], [])

    def test_over_50_lines_flagged(self):
        code = "x = 1\n" * 60
        result = review_code(code)
        self.assertTrue(result["ok"])
        self.assertTrue(any("50 lines" in i for i in result["issues"]))

    def test_factory_manager_service_controller_flagged(self):
        code = "class UserFactoryManagerServiceController:\n    pass\n"
        result = review_code(code)
        self.assertTrue(result["ok"])
        self.assertTrue(any("abstraction" in i.lower() for i in result["issues"]))

    def test_wildcard_import_flagged(self):
        code = "from os import *\n"
        result = review_code(code)
        self.assertTrue(result["ok"])
        self.assertTrue(any("wildcard" in i.lower() for i in result["issues"]))

    def test_deep_nesting_flagged(self):
        code = "if a:\n    if b:\n        if c:\n            if d:\n                if e:\n                    if f:\n                        pass\n"
        result = review_code(code)
        self.assertTrue(result["ok"])
        self.assertTrue(any("nesting" in i.lower() for i in result["issues"]))

    def test_returns_token_estimates(self):
        code = "x = 1\n" * 10
        result = review_code(code)
        self.assertIn("original_tokens", result)
        self.assertIn("compressed_tokens", result)
        self.assertIn("estimated_savings", result)
        self.assertIn("recommendation", result)
        self.assertIn("compressed_preview", result)


class TestGamification(unittest.TestCase):
    def test_level_calculation(self):
        g = Gamification(total_tokens_saved=25000)
        newly = g.check_achievements()
        self.assertEqual(g.level, 1 + 25000 // 10000)  # level 3

    def test_achievement_unlocks(self):
        g = Gamification(total_tokens_saved=5)
        newly = g.check_achievements()
        self.assertIn("first_savings", newly)

    def test_xp_for_tokens(self):
        g = Gamification()
        self.assertEqual(g.xp_for_tokens(100), 10)


# ---------------------------------------------------------------------------
# StateManager tests (use temp dir to avoid touching real state)
# ---------------------------------------------------------------------------

class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state_path = os.path.join(self.tmpdir, "state.json")
        self.lock_path = os.path.join(self.tmpdir, "state.lock")
        self.sm = StateManager(state_path=self.state_path)

    def test_enable_disable(self):
        state = self.sm.enable()
        self.assertTrue(state["enabled"])
        state = self.sm.disable()
        self.assertFalse(state["enabled"])

    def test_status_structure(self):
        self.sm.enable()
        status = self.sm.status()
        required_keys = {
            "enabled", "turns", "subagents_propagated", "original_chars",
            "compressed_chars", "saved_chars", "estimated_tokens_saved",
            "level", "xp", "current_streak", "best_streak",
            "achievements_unlocked", "total_achievements",
        }
        self.assertTrue(required_keys.issubset(set(status.keys())),
                        f"Missing keys: {required_keys - set(status.keys())}")

    def test_record_turn_accumulates(self):
        self.sm.record_turn(100, 60)
        self.sm.record_turn(200, 120)
        state = self.sm.load()
        self.assertEqual(state["total_original_chars"], 300)
        self.assertEqual(state["total_compressed_chars"], 180)
        self.assertEqual(state["turns"], 2)
        self.assertEqual(state["total_chars_saved"], 120)

    def test_domain_rule_never_compress(self):
        self.sm.set_domain_rule("security", "never_compress", True)
        rules = self.sm.get_domain_rules()
        self.assertIn("security", rules.never_compress)

    def test_domain_rule_always_compress(self):
        self.sm.set_domain_rule("docs", "always_compress", True)
        rules = self.sm.get_domain_rules()
        self.assertIn("docs", rules.always_compress)

    def test_domain_rule_force_preset(self):
        self.sm.set_domain_preset("commit", "commit")
        self.assertEqual(self.sm.get_domain_preset("commit"), "commit")

    def test_token_budget(self):
        self.sm.set_token_budget(5000)
        self.assertEqual(self.sm.get_token_budget(), 5000)

    def test_record_tokens_used_budget_alert(self):
        self.sm.set_token_budget(100)
        result = self.sm.record_tokens_used(85)  # 85% -> alert
        self.assertIsNotNone(result["alert"])
        self.assertEqual(result["used_today"], 85)

    def test_record_tokens_used_exceeds_budget(self):
        self.sm.set_token_budget(100)
        result = self.sm.record_tokens_used(120)  # exceeds budget
        self.assertIsNotNone(result["alert"])
        self.assertIn("reached", result["alert"])

    def test_project_type(self):
        self.sm.set_project_type("web")
        self.assertEqual(self.sm.get_project_type(), "web")

    def test_auto_learn_toggle(self):
        self.sm.set_auto_learn(False)
        state = self.sm.load()
        self.assertFalse(state["auto_learn"])

    def test_record_learned_pattern(self):
        self.sm.record_learned_pattern("test_pattern", reverted=True)
        state = self.sm.load()
        self.assertIn("test_pattern", state["learned_patterns"])
        self.assertEqual(state["learned_patterns"]["test_pattern"]["revert_count"], 1)

    def test_should_compress_pattern_default_true(self):
        self.assertTrue(self.sm.should_compress_pattern("unknown_pattern"))

    def test_check_achievements(self):
        # Manually set high token savings
        state = self.sm.load()
        state["total_tokens_saved"] = 5
        self.sm.save(state)
        newly = self.sm.check_achievements()
        self.assertIn("first_savings", newly)

    def test_reset_clears_state(self):
        self.sm.enable()
        self.sm.record_turn(100, 60)
        self.sm.reset()
        state = self.sm.load()
        self.assertFalse(state["enabled"])
        self.assertEqual(state["turns"], 0)

    def test_persistence_across_instances(self):
        self.sm.enable()
        sm2 = StateManager(state_path=self.state_path)
        state = sm2.load()
        self.assertTrue(state["enabled"])


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestIntegration(unittest.TestCase):
    def test_compress_prose_reduces_tokens(self):
        text = "This is a really long piece of prose that basically just says hello."
        compressed = compress_prose(text)
        orig_tokens = estimate_tokens(text)
        comp_tokens = estimate_tokens(compressed)
        self.assertLessEqual(comp_tokens, orig_tokens)

    def test_review_code_on_overengineered_class(self):
        code = """
class UserFactoryManagerServiceController:
    def __init__(self):
        self.factory = UserFactory()
        self.manager = UserManager()
    def process(self, data):
        if data:
            if data.get("users"):
                for user in data["users"]:
                    if user.get("active"):
                        result = self.factory.create(user)
                        self.manager.handle(result)
        return True
"""
        result = review_code(code)
        self.assertTrue(result["ok"])
        self.assertGreater(len(result["issues"]), 0)
        self.assertGreater(result["estimated_savings"], 0)


if __name__ == "__main__":
    unittest.main()
