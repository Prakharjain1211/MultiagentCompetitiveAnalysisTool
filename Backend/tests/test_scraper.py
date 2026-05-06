"""Tests for src.tools.scraper module."""

import pytest
from unittest.mock import patch, MagicMock

from src.tools.scraper import WebScraper, MAX_PAGE_SIZE


class TestWebScraperInit:
    def test_init_creates_session(self):
        scraper = WebScraper()
        assert scraper.session is not None
        assert scraper._robot_parsers == {}


class TestWebScraperGetUserAgent:
    @patch("src.tools.scraper.settings")
    def test_returns_user_agent_from_settings(self, mock_settings):
        mock_settings.user_agents = ["UA1", "UA2", "UA3"]
        scraper = WebScraper()
        ua = scraper._get_user_agent()
        assert ua in ["UA1", "UA2", "UA3"]


class TestWebScraperScrape:
    @patch.object(WebScraper, "_check_robots", return_value=True)
    @patch("requests.Session")
    def test_successful_scrape(self, mock_session_cls, mock_robots):
        mock_resp = MagicMock()
        mock_resp.text = "<html><body><p>Hello World</p></body></html>"
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_resp
        mock_session_cls.return_value = mock_session

        scraper = WebScraper()
        result = scraper.scrape("https://example.com")

        assert result["success"] is True
        assert result["url"] == "https://example.com"
        assert result["error"] == ""
        assert "Hello World" in result["content"]

    @patch.object(WebScraper, "_check_robots", return_value=True)
    @patch("requests.Session")
    def test_handles_http_error(self, mock_session_cls, mock_robots):
        import requests
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.RequestException("Connection error")
        mock_session_cls.return_value = mock_session

        scraper = WebScraper()
        result = scraper.scrape("https://example.com")

        assert result["success"] is False
        assert result["content"] == ""
        assert "Connection error" in result["error"]

    @patch.object(WebScraper, "_check_robots", return_value=False)
    def test_blocked_by_robots_txt(self, mock_robots):
        scraper = WebScraper()
        result = scraper.scrape("https://example.com")

        assert result["success"] is False
        assert result["error"] == "Blocked by robots.txt"

    @patch.object(WebScraper, "_check_robots", return_value=True)
    @patch("requests.Session")
    def test_truncates_large_response(self, mock_session_cls, mock_robots):
        large_html = "<p>" + "A" * (MAX_PAGE_SIZE + 1000) + "</p>"
        mock_resp = MagicMock()
        mock_resp.text = large_html
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_resp
        mock_session_cls.return_value = mock_session

        scraper = WebScraper()
        result = scraper.scrape("https://example.com")

        assert result["success"] is True
        assert len(result["content"]) <= MAX_PAGE_SIZE

    @patch.object(WebScraper, "_check_robots", return_value=True)
    @patch("requests.Session")
    def test_passes_timeout_parameter(self, mock_session_cls, mock_robots):
        mock_resp = MagicMock()
        mock_resp.text = "<p>Test</p>"
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_resp
        mock_session_cls.return_value = mock_session

        scraper = WebScraper()
        scraper.scrape("https://example.com", timeout=5)

        mock_session.get.assert_called_once()
        call_kwargs = mock_session.get.call_args[1]
        assert call_kwargs["timeout"] == 5
