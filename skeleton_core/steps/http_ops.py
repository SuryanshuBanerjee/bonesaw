"""
HTTP operation steps for Bonesaw.

Provides steps for making HTTP requests, downloading files, and calling APIs.
"""

import logging
from pathlib import Path
from typing import Any, Optional

import requests

from skeleton_core.config import register_step

logger = logging.getLogger(__name__)


@register_step("http_get")
class HTTPGetStep:
    """
    Make an HTTP GET request.

    Input: str (URL) or None if URL provided
    Output: str (response text)
    Context: Writes 'status_code', 'response_size', 'url'
    """

    def __init__(self, url: Optional[str] = None, headers: Optional[dict[str, str]] = None, timeout: int = 30):
        """
        Args:
            url: URL to request (optional if passed via data)
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
        """
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Make GET request."""
        url = self.url or data

        logger.info(f"GET {url}")

        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()

        context['status_code'] = response.status_code
        context['response_size'] = len(response.text)
        context['url'] = url

        logger.info(f"Response: {response.status_code} ({len(response.text)} bytes)")
        return response.text


@register_step("http_post")
class HTTPPostStep:
    """
    Make an HTTP POST request.

    Input: dict (JSON body) or None if data provided
    Output: str (response text)
    Context: Writes 'status_code', 'response_size', 'url'
    """

    def __init__(
        self,
        url: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: int = 30
    ):
        """
        Args:
            url: URL to request
            data: Optional JSON data (can be passed via pipeline)
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
        """
        self.url = url
        self.data = data
        self.headers = headers or {}
        self.timeout = timeout

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Make POST request."""
        json_data = self.data or data

        logger.info(f"POST {self.url}")

        response = requests.post(
            self.url,
            json=json_data,
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()

        context['status_code'] = response.status_code
        context['response_size'] = len(response.text)
        context['url'] = self.url

        logger.info(f"Response: {response.status_code} ({len(response.text)} bytes)")
        return response.text


@register_step("download_file")
class DownloadFileStep:
    """
    Download a file from a URL.

    Input: str (URL) or None if URL provided
    Output: str (path to downloaded file)
    Context: Writes 'file_size', 'download_url', 'download_path'
    """

    def __init__(self, url: Optional[str] = None, output_path: Optional[str] = None, timeout: int = 60):
        """
        Args:
            url: URL to download (optional if passed via data)
            output_path: Where to save file (optional, uses filename from URL)
            timeout: Download timeout in seconds
        """
        self.url = url
        self.output_path = output_path
        self.timeout = timeout

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Download file."""
        url = self.url or data

        # Determine output path
        if self.output_path:
            output_path = Path(self.output_path)
        else:
            filename = url.split('/')[-1] or 'download'
            output_path = Path(filename)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading {url} -> {output_path}")

        response = requests.get(url, timeout=self.timeout, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = output_path.stat().st_size
        context['file_size'] = file_size
        context['download_url'] = url
        context['download_path'] = str(output_path)

        logger.info(f"Downloaded {file_size} bytes to {output_path}")
        return str(output_path)


@register_step("webhook")
class WebhookStep:
    """
    Send data to a webhook URL.

    Input: dict (payload) or None if payload provided
    Output: str (response text)
    Context: Writes 'status_code', 'webhook_url'
    """

    def __init__(self, url: str, payload: Optional[dict[str, Any]] = None, timeout: int = 30):
        """
        Args:
            url: Webhook URL
            payload: Optional payload (can be passed via pipeline)
            timeout: Request timeout in seconds
        """
        self.url = url
        self.payload = payload
        self.timeout = timeout

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Send webhook."""
        payload = self.payload or data

        logger.info(f"Sending webhook to {self.url}")

        response = requests.post(self.url, json=payload, timeout=self.timeout)
        response.raise_for_status()

        context['status_code'] = response.status_code
        context['webhook_url'] = self.url

        logger.info(f"Webhook sent: {response.status_code}")
        return response.text
