from django.test import TestCase

from core import ai_service
from core.token_reduction import (
    LlmCache,
    distill,
    estimate_tokens,
    make_cache_key,
    split_text,
    truncate,
)


class TokenReductionTests(TestCase):
    def test_estimate_tokens_returns_positive(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertGreater(estimate_tokens("some short text"), 0)

    def test_truncate_fits_budget(self):
        text = "The business objective is to reduce customer churn. " * 100
        result = truncate(text, 64)
        self.assertLessEqual(estimate_tokens(result), 64)

    def test_truncate_short_text_unchanged(self):
        text = "short"
        self.assertEqual(truncate(text, 100), text)

    def test_split_text_produces_bounded_chunks(self):
        text = "The business objective is to predict churn accurately. " * 500
        chunks = split_text(text, chunk_tokens=200, overlap_tokens=20)
        self.assertGreaterEqual(len(chunks), 2)
        for chunk in chunks:
            self.assertLessEqual(estimate_tokens(chunk), 200)

    def test_distill_fits_target(self):
        text = (
            "The business objective is to reduce churn. ROI is 3.5x. "
            "Timeline is 6 weeks. " * 200
        )
        result = distill(text, 150)
        self.assertLessEqual(estimate_tokens(result), 150)

    def test_distill_short_text_unchanged(self):
        text = "The business objective is clear."
        self.assertEqual(distill(text, 500), text)


class LlmCacheTests(TestCase):
    def test_set_get_roundtrip(self):
        cache = LlmCache()
        cache.set("k1", "v1")
        self.assertEqual(cache.get("k1"), "v1")
        self.assertEqual(cache.size, 1)

    def test_missing_key_returns_none(self):
        self.assertIsNone(LlmCache().get("nope"))

    def test_bounded_eviction(self):
        cache = LlmCache(max_entries=2)
        cache.set("a", "1")
        cache.set("b", "2")
        cache.set("c", "3")
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.size, 2)

    def test_make_cache_key_is_deterministic(self):
        a = make_cache_key("gemini", "m", "s", "u", 0.4, 100, None)
        b = make_cache_key("gemini", "m", "s", "u", 0.4, 100, None)
        self.assertEqual(a, b)


class AiServiceRoutingTests(TestCase):
    def setUp(self):
        self._provider = ai_service.get_provider()
        self._cache = ai_service.get_cache()
        self._cache.clear()

    def tearDown(self):
        self._cache.clear()

    def test_mock_fallback_with_placeholder_keys(self):
        ai_service.get_cache().clear()
        text = ai_service._call_llm(
            user_prompt="hello",
            system_prompt="You are an AI consulting expert.",
        )
        self.assertTrue(text)

    def test_call_llm_is_cached(self):
        ai_service.get_cache().clear()
        first = ai_service._call_llm(
            user_prompt="hello",
            system_prompt="You are an AI consulting expert.",
        )
        second = ai_service._call_llm(
            user_prompt="hello",
            system_prompt="You are an AI consulting expert.",
        )
        self.assertEqual(first, second)
        self.assertGreater(ai_service.get_cache().size, 0)

    def test_get_llm_client_mock_without_keys(self):
        self.assertIn(
            type(ai_service.get_llm_client()).__name__,
            ("_MockLLMClient", "_GeminiClient", "_AirLLMClient"),
        )

    def test_airllm_config_helpers(self):
        self.assertEqual(ai_service.get_airllm_model().strip(), ai_service.get_airllm_model().strip())
        self.assertIn(ai_service.is_airllm_configured(), (True, False))
