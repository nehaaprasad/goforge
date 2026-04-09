"""Tests for remote git URL validation (SSRF guards)."""

import socket
from unittest import TestCase
from unittest.mock import patch

from goforge.repo.remote_clone import (
    _DEFAULT_ALLOWED,
    validate_remote_git_url,
)


class TestRemoteUrlValidation(TestCase):
    @patch("goforge.repo.remote_clone.socket.getaddrinfo")
    def test_accepts_https_github_with_public_dns(self, mock_gai: object) -> None:
        # Public unicast address (mocked — avoids depending on real DNS in CI).
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))
        ]
        u = validate_remote_git_url(
            "https://github.com/octocat/Hello-World.git",
            allowed_hosts=_DEFAULT_ALLOWED,
        )
        self.assertEqual(
            u, "https://github.com/octocat/Hello-World.git"
        )

    def test_rejects_http(self) -> None:
        with self.assertRaises(ValueError):
            validate_remote_git_url(
                "http://github.com/a/b",
                allowed_hosts=_DEFAULT_ALLOWED,
            )

    def test_rejects_file_scheme(self) -> None:
        with self.assertRaises(ValueError):
            validate_remote_git_url(
                "file:///etc/passwd",
                allowed_hosts=_DEFAULT_ALLOWED,
            )

    def test_rejects_credentials_in_url(self) -> None:
        with self.assertRaises(ValueError):
            validate_remote_git_url(
                "https://user:pass@github.com/foo/bar.git",
                allowed_hosts=_DEFAULT_ALLOWED,
            )

    def test_rejects_unknown_host(self) -> None:
        with self.assertRaises(ValueError):
            validate_remote_git_url(
                "https://evil.example.com/a/b.git",
                allowed_hosts=_DEFAULT_ALLOWED,
            )

    @patch("goforge.repo.remote_clone.socket.getaddrinfo")
    def test_rejects_loopback_resolution(self, mock_gai: object) -> None:
        mock_gai.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))
        ]
        with self.assertRaises(ValueError):
            validate_remote_git_url(
                "https://github.com/foo/bar.git",
                allowed_hosts=frozenset({"github.com"}),
            )
