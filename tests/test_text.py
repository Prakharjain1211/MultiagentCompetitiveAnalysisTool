"""Tests for src.utils.text module."""

import pytest
from src.utils.text import clean_html, truncate, split_sentences


class TestCleanHtml:
    def test_strips_simple_html_tags(self):
        html = "<p>Hello <b>world</b></p>"
        assert clean_html(html) == "Hello world"

    def test_removes_script_and_style(self):
        html = "<div><script>alert(1)</script><p>Content</p></div>"
        result = clean_html(html)
        assert "alert" not in result
        assert "Content" in result

    def test_removes_nav_footer_header_aside(self):
        html = "<nav>Menu</nav><main>Body</main><footer>Foot</footer>"
        result = clean_html(html)
        assert "Menu" not in result
        assert "Body" in result
        assert "Foot" not in result

    def test_collapses_whitespace(self):
        html = "<p>Hello   world\n\n\n  test</p>"
        assert clean_html(html) == "Hello world test"

    def test_strips_leading_trailing_whitespace(self):
        html = "  <p> text </p>  "
        assert clean_html(html) == "text"

    def test_empty_string(self):
        assert clean_html("") == ""

    def test_plain_text_passthrough(self):
        assert clean_html("Hello world") == "Hello world"


class TestTruncate:
    def test_no_truncation_when_under_limit(self):
        text = "Hello world"
        assert truncate(text, 100) == "Hello world"

    def test_truncates_at_word_boundary(self):
        text = "Hello world foo bar"
        result = truncate(text, 11)
        assert result.startswith("Hello")
        assert result.endswith("...")
        assert "world" not in result.split("...")[0]

    def test_does_not_split_word(self):
        text = "The quick brown fox"
        result = truncate(text, 10)
        assert " " not in result.split("...")[0][-1] if "..." in result else True

    def test_exact_length(self):
        text = "Hello"
        assert truncate(text, 5) == "Hello"

    def test_very_short_limit(self):
        text = "Hello world"
        result = truncate(text, 3)
        assert result.endswith("...")

    def test_empty_string(self):
        assert truncate("", 10) == ""


class TestSplitSentences:
    def test_splits_on_period(self):
        text = "Hello. World. Test."
        result = split_sentences(text)
        assert result == ["Hello.", "World.", "Test."]

    def test_splits_on_exclamation(self):
        text = "Wow! Amazing!"
        assert split_sentences(text) == ["Wow!", "Amazing!"]

    def test_splits_on_question_mark(self):
        text = "Who? What?"
        assert split_sentences(text) == ["Who?", "What?"]

    def test_filters_empty_strings(self):
        text = "Hello.  . World."
        result = split_sentences(text)
        assert "" not in result

    def test_strips_whitespace(self):
        text = "Hello.   World."
        assert split_sentences(text) == ["Hello.", "World."]

    def test_single_sentence(self):
        assert split_sentences("Hello world") == ["Hello world"]

    def test_empty_string(self):
        assert split_sentences("") == []
