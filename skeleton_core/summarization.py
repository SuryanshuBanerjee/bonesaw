"""
Summarization utilities for Bonesaw pipelines.

Provides deterministic, data-driven summaries with optional LLM enhancement.
Falls back gracefully to template-based summaries if LLM is not configured.
"""

from __future__ import annotations

import json
import logging
import os
import textwrap
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)


@dataclass
class SummarizationConfig:
    """Configuration for summarization mode."""
    provider: str | None
    api_key: str | None
    model: str | None
    use_llm_flag: bool


def get_summarization_config(context: dict[str, Any] | None = None) -> SummarizationConfig:
    """
    Determine summarization configuration from environment and context.
    
    Args:
        context: Pipeline context dictionary (may contain 'use_llm' flag)
        
    Returns:
        SummarizationConfig with provider, API key, model, and flag status
    """
    ctx = context or {}
    provider = os.getenv("BONESAW_LLM_PROVIDER") or None
    api_key = os.getenv("BONESAW_LLM_API_KEY") or None
    model = os.getenv("BONESAW_LLM_MODEL") or None
    use_llm_flag = bool(ctx.get("use_llm"))
    
    return SummarizationConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        use_llm_flag=use_llm_flag
    )


def llm_enabled(config: SummarizationConfig) -> bool:
    """
    Check if LLM summarization is fully enabled.
    
    Requires all four conditions:
    - use_llm flag is True
    - provider is configured
    - model is configured
    - API key is configured
    """
    return bool(config.use_llm_flag and config.provider and config.model and config.api_key)


def template_log_summary(stats: dict[str, Any]) -> str:
    """
    Build a deterministic, data-driven summary for logs based on aggregated stats.
    
    Args:
        stats: Dictionary with 'total', 'by_level', and 'logs' keys
        
    Returns:
        Multi-line summary string
    """
    total = stats.get("total", 0)
    by_level: dict[str, int] = stats.get("by_level", {})
    levels_sorted = sorted(by_level.items(), key=lambda kv: kv[1], reverse=True)
    dominant_level = levels_sorted[0][0] if levels_sorted else "UNKNOWN"
    sample_logs: list[dict[str, Any]] = stats.get("logs", [])[:3]
    
    sample_lines: list[str] = []
    for entry in sample_logs:
        ts = entry.get("timestamp", "?")
        level = entry.get("level", "?")
        msg = entry.get("message", "")[:120]
        sample_lines.append(f"- [{level}] {ts}: {msg}")
    
    summary_lines = [
        f"The system emitted {total} log entries across {len(by_level)} levels.",
        f"The dominant level appears to be {dominant_level}.",
    ]
    
    if "ERROR" in by_level:
        summary_lines.append(
            f"There are {by_level['ERROR']} ERROR-level events that may need attention."
        )
    
    if sample_lines:
        summary_lines.append("Recent notable entries:")
        summary_lines.extend(sample_lines)
    
    return "\n".join(summary_lines)


def template_feed_summary(entries: list[dict[str, Any]]) -> str:
    """
    Build a deterministic, data-driven summary for feed entries.
    
    Args:
        entries: List of normalized feed entry dictionaries
        
    Returns:
        Multi-line summary string
    """
    total = len(entries)
    if total == 0:
        return "No entries were found in the configured feeds."
    
    # Count entries by feed_title
    counts: dict[str, int] = {}
    for e in entries:
        ft = e.get("feed_title") or "Unknown Feed"
        counts[ft] = counts.get(ft, 0) + 1
    top_feeds = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:3]
    
    # Sample entry titles
    sample = entries[:3]
    sample_titles = [
        f"- {e.get('feed_title', 'Unknown Feed')}: {e.get('entry_title', 'Untitled')[:120]}"
        for e in sample
    ]
    
    summary_lines = [
        f"Collected {total} entries from {len(counts)} feeds.",
    ]
    
    if top_feeds:
        top_str = ", ".join(f"{name} ({count})" for name, count in top_feeds)
        summary_lines.append(f"The most active sources include: {top_str}.")
    
    if sample_titles:
        summary_lines.append("Sample entries:")
        summary_lines.extend(sample_titles)
    
    return "\n".join(summary_lines)


def _call_llm(provider: str, api_key: str, model: str, prompt: str) -> str:
    """
    Call an LLM provider to generate a summary.
    
    Currently supports OpenRouter with real API calls. Other providers fall back
    to simulated responses. Never raises exceptions - always returns a string.
    
    Args:
        provider: LLM provider name (e.g., "openrouter", "openai", "anthropic")
        api_key: API key for authentication
        model: Model name (e.g., "anthropic/claude-3-sonnet", "gpt-3.5-turbo")
        prompt: Prompt text to send to the LLM
        
    Returns:
        LLM-generated text, or simulated fallback if call fails
    """
    # OpenRouter integration
    if provider == "openrouter":
        if not api_key or not model:
            logger.warning("OpenRouter selected but missing api_key or model; using simulated response")
            return _simulated_response(provider, model, prompt)
        
        try:
            logger.info("Calling OpenRouter with model=%s", model)
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://example.com",
                    "X-Title": "bonesaw-pipeline"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=15
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                logger.warning(
                    "OpenRouter call failed with status %d; falling back to simulated summary",
                    response.status_code
                )
                return _simulated_response(provider, model, prompt)
            
            # Parse response
            data = response.json()
            
            # Extract content from OpenRouter response format
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                if content:
                    logger.info("OpenRouter call succeeded with model %s", model)
                    return content
                else:
                    logger.warning("OpenRouter returned empty content; using simulated response")
                    return _simulated_response(provider, model, prompt)
            else:
                logger.warning("OpenRouter response missing expected structure; using simulated response")
                return _simulated_response(provider, model, prompt)
                
        except requests.exceptions.Timeout:
            logger.warning("OpenRouter call timed out; falling back to simulated summary")
            return _simulated_response(provider, model, prompt)
        except requests.exceptions.RequestException as exc:
            logger.warning("OpenRouter call failed (%s); falling back to simulated summary", exc)
            return _simulated_response(provider, model, prompt)
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("Failed to parse OpenRouter response (%s); falling back to simulated summary", exc)
            return _simulated_response(provider, model, prompt)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Unexpected error calling OpenRouter (%s); falling back to simulated summary", exc)
            return _simulated_response(provider, model, prompt)
    
    # Other providers not yet implemented
    else:
        logger.info("LLM provider %s not implemented yet; returning simulated summary", provider)
        return _simulated_response(provider, model, prompt)


def _simulated_response(provider: str, model: str, prompt: str) -> str:
    """
    Generate a simulated LLM response for fallback scenarios.
    
    Args:
        provider: Provider name
        model: Model name
        prompt: Original prompt
        
    Returns:
        Simulated response string
    """
    trimmed = textwrap.shorten(
        prompt.replace("\n", " "),
        width=400,
        placeholder=" ..."
    )
    return f"[Simulated LLM summary via {provider}:{model or 'unknown'} based on: {trimmed}]"


def summarize_logs(stats: dict[str, Any], context: dict[str, Any] | None = None) -> str:
    """
    Generate a summary of log statistics with optional LLM enhancement.
    
    Always produces a deterministic template-based summary. If LLM is enabled
    and configured, appends an LLM-generated summary. Falls back gracefully
    if LLM call fails.
    
    Args:
        stats: Aggregated log statistics from AggregateErrorsStep
        context: Pipeline context (may contain 'use_llm' flag)
        
    Returns:
        Summary text (deterministic, or deterministic + LLM)
    """
    config = get_summarization_config(context)
    base_summary = template_log_summary(stats)
    
    if not llm_enabled(config):
        # Log specific reasons why LLM is not enabled
        if config.use_llm_flag:
            missing = []
            if not config.provider:
                missing.append("BONESAW_LLM_PROVIDER")
            if not config.model:
                missing.append("BONESAW_LLM_MODEL")
            if not config.api_key:
                missing.append("BONESAW_LLM_API_KEY")
            
            if missing:
                logger.warning(
                    "LLM requested but missing configuration: %s. Falling back to deterministic summary.",
                    ", ".join(missing)
                )
        else:
            logger.debug("LLM not enabled for log summarization")
        return base_summary
    
    try:
        prompt = (
            f"You are summarizing system logs. Here are the aggregated stats as JSON:\n"
            f"{json.dumps(stats, default=str)[:2000]}\n\n"
            f"Write a brief 2-3 sentence summary."
        )
        llm_text = _call_llm(
            config.provider or "unknown",
            config.api_key or "",
            config.model or "unknown",
            prompt
        )
        return base_summary + "\n\n---\n\n" + llm_text
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM summarization failed, falling back to template only: %s", exc)
        return base_summary


def summarize_text(lines: list[str], context: dict[str, Any] | None = None) -> str:
    """
    Generate a summary of text lines with optional LLM enhancement.
    
    Always produces a deterministic template-based summary. If LLM is enabled
    and configured, appends an LLM-generated summary. Falls back gracefully
    if LLM call fails.
    
    Args:
        lines: List of text lines to summarize
        context: Pipeline context (may contain 'use_llm' flag)
        
    Returns:
        Summary text (deterministic, or deterministic + LLM)
    """
    config = get_summarization_config(context)
    
    # Build deterministic template summary
    total_lines = len(lines)
    sample_lines = lines[:3]
    
    summary_parts = [
        f"The pipeline processed {total_lines} lines of text.",
    ]
    
    if sample_lines:
        summary_parts.append("Sample lines:")
        for line in sample_lines:
            # Truncate long lines
            display_line = line[:100] + "..." if len(line) > 100 else line
            summary_parts.append(f"  - {display_line}")
    
    summary_parts.append(
        "The transformed text has been captured in the spectral realm of the pipeline... 👻"
    )
    
    base_summary = "\n".join(summary_parts)
    
    if not llm_enabled(config):
        # Log specific reasons why LLM is not enabled
        if config.use_llm_flag:
            missing = []
            if not config.provider:
                missing.append("BONESAW_LLM_PROVIDER")
            if not config.model:
                missing.append("BONESAW_LLM_MODEL")
            if not config.api_key:
                missing.append("BONESAW_LLM_API_KEY")
            
            if missing:
                logger.warning(
                    "LLM requested but missing configuration: %s. Falling back to deterministic summary.",
                    ", ".join(missing)
                )
        else:
            logger.debug("LLM not enabled for text summarization")
        return base_summary
    
    try:
        # Prepare text for LLM (truncate if very long)
        text_sample = "\n".join(lines[:50])  # First 50 lines
        if len(text_sample) > 2000:
            text_sample = text_sample[:2000] + "\n... (truncated)"
        
        prompt = (
            f"You are an assistant summarizing pipeline output text.\n\n"
            f"Given the following processed text lines:\n\n{text_sample}\n\n"
            f"Produce:\n"
            f"- 3 short bullet points summarizing the content\n"
            f"- 1 spooky or eerie closing sentence\n\n"
            f"Avoid leaking any secrets; speak generally about the content."
        )
        
        llm_text = _call_llm(
            config.provider or "unknown",
            config.api_key or "",
            config.model or "unknown",
            prompt
        )
        return base_summary + "\n\n---\n\n" + llm_text
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM summarization for text failed, falling back to template only: %s", exc)
        return base_summary


def summarize_feeds(entries: list[dict[str, Any]], context: dict[str, Any] | None = None) -> str:
    """
    Generate a summary of feed entries with optional LLM enhancement.
    
    Always produces a deterministic template-based summary. If LLM is enabled
    and configured, appends an LLM-generated summary. Falls back gracefully
    if LLM call fails.
    
    Args:
        entries: List of normalized feed entries
        context: Pipeline context (may contain 'use_llm' flag)
        
    Returns:
        Summary text (deterministic, or deterministic + LLM)
    """
    config = get_summarization_config(context)
    base_summary = template_feed_summary(entries)
    
    if not llm_enabled(config):
        # Log specific reasons why LLM is not enabled
        if config.use_llm_flag:
            missing = []
            if not config.provider:
                missing.append("BONESAW_LLM_PROVIDER")
            if not config.model:
                missing.append("BONESAW_LLM_MODEL")
            if not config.api_key:
                missing.append("BONESAW_LLM_API_KEY")
            
            if missing:
                logger.warning(
                    "LLM requested but missing configuration: %s. Falling back to deterministic summary.",
                    ", ".join(missing)
                )
        else:
            logger.debug("LLM not enabled for feed summarization")
        return base_summary
    
    try:
        sample_for_prompt = entries[:10]
        prompt = (
            f"You are summarizing RSS/Atom feed entries. Here is a JSON snippet of entries:\n"
            f"{json.dumps(sample_for_prompt, default=str)[:2000]}\n\n"
            f"Write a brief 2-3 sentence overview."
        )
        llm_text = _call_llm(
            config.provider or "unknown",
            config.api_key or "",
            config.model or "unknown",
            prompt
        )
        return base_summary + "\n\n---\n\n" + llm_text
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM summarization for feeds failed, falling back to template only: %s", exc)
        return base_summary
