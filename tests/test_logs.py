"""
Tests for Haunted Log Cleaner pipeline steps.

Tests parsing and anonymization functionality.
"""

from apps.haunted_log_cleaner.pipelines import AnonymizeLogsStep, ParseLogsStep


def test_parse_logs_step():
    """Test that ParseLogsStep correctly parses valid log lines."""
    step = ParseLogsStep()
    
    lines = [
        "2025-10-31 23:45:12 [INFO] User john@example.com logged in\n",
        "2025-10-31 23:46:03 [WARNING] High memory usage detected\n",
    ]
    
    context = {}
    result = step.run(lines, context)
    
    # Should parse both lines
    assert len(result) == 2
    
    # Check first parsed entry
    first = result[0]
    assert first["timestamp"] == "2025-10-31 23:45:12"
    assert first["level"] == "INFO"
    assert "john@example.com" in first["message"]
    assert "logged in" in first["message"]
    
    # Check second parsed entry
    second = result[1]
    assert second["timestamp"] == "2025-10-31 23:46:03"
    assert second["level"] == "WARNING"
    assert "High memory usage" in second["message"]
    
    # Check context was updated
    assert context["parsed_count"] == 2
    assert context["skipped_count"] == 0


def test_parse_logs_step_skips_invalid_lines():
    """Test that ParseLogsStep skips lines that don't match the format."""
    step = ParseLogsStep()
    
    lines = [
        "2025-10-31 23:45:12 [INFO] Valid line\n",
        "This is not a valid log line\n",
        "2025-10-31 23:46:03 [ERROR] Another valid line\n",
    ]
    
    context = {}
    result = step.run(lines, context)
    
    # Should parse only 2 valid lines
    assert len(result) == 2
    assert context["parsed_count"] == 2
    assert context["skipped_count"] == 1


def test_anonymize_logs_step():
    """Test that AnonymizeLogsStep redacts emails and IP addresses."""
    step = AnonymizeLogsStep()
    
    logs = [
        {
            "timestamp": "2025-10-31 23:45:12",
            "level": "INFO",
            "message": "Email user@example.com accessed from 192.168.0.1"
        },
        {
            "timestamp": "2025-10-31 23:46:03",
            "level": "WARNING",
            "message": "Connection from 10.0.0.50 to admin@system.org"
        }
    ]
    
    context = {}
    result = step.run(logs, context)
    
    # Should have same number of entries
    assert len(result) == 2
    
    # Check first entry is anonymized
    first = result[0]
    assert "[REDACTED]" in first["message"]
    assert "user@example.com" not in first["message"]
    assert "192.168.0.1" not in first["message"]
    
    # Check second entry is anonymized
    second = result[1]
    assert "[REDACTED]" in second["message"]
    assert "10.0.0.50" not in second["message"]
    assert "admin@system.org" not in second["message"]
    
    # Check context shows redactions occurred
    assert context["anonymized_count"] == 2


def test_anonymize_logs_step_preserves_clean_messages():
    """Test that AnonymizeLogsStep doesn't modify messages without sensitive data."""
    step = AnonymizeLogsStep()
    
    logs = [
        {
            "timestamp": "2025-10-31 23:45:12",
            "level": "INFO",
            "message": "System startup completed successfully"
        }
    ]
    
    context = {}
    result = step.run(logs, context)
    
    # Message should be unchanged
    assert result[0]["message"] == "System startup completed successfully"
    assert context["anonymized_count"] == 0
