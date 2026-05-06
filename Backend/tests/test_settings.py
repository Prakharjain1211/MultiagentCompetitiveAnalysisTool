"""Tests for config.settings module."""

import pytest
from config.settings import Settings


class TestSettings:
    def test_default_openai_api_key(self):
        s = Settings(_env_file=None)
        assert s.openai_api_key == ""

    def test_default_tavily_api_key(self):
        s = Settings(_env_file=None)
        assert s.tavily_api_key == ""

    def test_default_max_retries(self):
        s = Settings(_env_file=None)
        assert s.max_retries == 3

    def test_default_max_chunk_size(self):
        s = Settings(_env_file=None)
        assert s.max_chunk_size == 500

    def test_default_chunk_overlap(self):
        s = Settings(_env_file=None)
        assert s.chunk_overlap == 50

    def test_default_top_k_retrieval(self):
        s = Settings(_env_file=None)
        assert s.top_k_retrieval == 3

    def test_user_agents_not_empty(self):
        s = Settings(_env_file=None)
        assert len(s.user_agents) >= 4

    def test_user_agents_are_strings(self):
        s = Settings(_env_file=None)
        for ua in s.user_agents:
            assert isinstance(ua, str)
            assert len(ua) > 0

    def test_singleton_settings_exists(self):
        from config.settings import settings
        assert settings is not None
        assert isinstance(settings, Settings)
