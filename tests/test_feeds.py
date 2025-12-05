"""
Tests for Graveyard Feed Reviver pipeline steps.

Tests JSON and markdown output generation (no network calls).
"""

import json

from apps.graveyard_feed_reviver.pipelines import WriteJSONStep, WriteMarkdownStep


def test_write_json_step(tmp_path):
    """Test that WriteJSONStep correctly writes entries to JSON file."""
    entries = [
        {
            "feed_title": "Test Feed",
            "entry_title": "Test Entry 1",
            "link": "https://example.com/1",
            "published": "2025-10-31",
            "summary": "First spooky test entry."
        },
        {
            "feed_title": "Test Feed",
            "entry_title": "Test Entry 2",
            "link": "https://example.com/2",
            "published": "2025-11-01",
            "summary": "Second spooky test entry."
        }
    ]
    
    json_path = tmp_path / "feeds.json"
    step = WriteJSONStep(output_path=str(json_path))
    
    context = {}
    result = step.run(entries, context)
    
    # Should return the same entries (pass-through)
    assert result == entries
    
    # File should exist
    assert json_path.exists()
    
    # Load and verify JSON content
    with open(json_path, 'r', encoding='utf-8') as f:
        loaded = json.load(f)
    
    assert len(loaded) == 2
    assert loaded[0]["entry_title"] == "Test Entry 1"
    assert loaded[1]["entry_title"] == "Test Entry 2"
    
    # Context should be updated
    assert context["json_path"] == str(json_path)


def test_write_markdown_step(tmp_path):
    """Test that WriteMarkdownStep correctly writes entries to markdown file."""
    entries = [
        {
            "feed_title": "Test Feed",
            "entry_title": "Test Entry 1",
            "link": "https://example.com/1",
            "published": "2025-10-31",
            "summary": "First spooky test entry."
        },
        {
            "feed_title": "Test Feed",
            "entry_title": "Test Entry 2",
            "link": "https://example.com/2",
            "published": "2025-11-01",
            "summary": "Second spooky test entry."
        }
    ]
    
    md_path = tmp_path / "feeds.md"
    step = WriteMarkdownStep(output_path=str(md_path))
    
    context = {}
    result = step.run(entries, context)
    
    # Should return the same entries (pass-through)
    assert result == entries
    
    # File should exist
    assert md_path.exists()
    
    # Read and verify markdown content
    content = md_path.read_text(encoding='utf-8')
    
    # Should contain the title
    assert "☠️ Graveyard Feed Reviver" in content
    
    # Should contain both entry titles
    assert "Test Entry 1" in content
    assert "Test Entry 2" in content
    
    # Should contain the feed title
    assert "Test Feed" in content
    
    # Should contain links
    assert "https://example.com/1" in content
    assert "https://example.com/2" in content
    
    # Context should be updated
    assert context["markdown_path"] == str(md_path)


def test_write_json_with_unicode(tmp_path):
    """Test that WriteJSONStep handles Unicode characters (emoji) correctly."""
    entries = [
        {
            "feed_title": "Spooky Feed 👻",
            "entry_title": "Halloween Special 🎃",
            "link": "https://example.com/spooky",
            "published": "2025-10-31",
            "summary": "Very spooky content with emoji! 💀🦴"
        }
    ]
    
    json_path = tmp_path / "unicode_feeds.json"
    step = WriteJSONStep(output_path=str(json_path))
    
    context = {}
    step.run(entries, context)
    
    # Load and verify Unicode is preserved
    with open(json_path, 'r', encoding='utf-8') as f:
        loaded = json.load(f)
    
    assert loaded[0]["feed_title"] == "Spooky Feed 👻"
    assert loaded[0]["entry_title"] == "Halloween Special 🎃"
    assert "💀🦴" in loaded[0]["summary"]
