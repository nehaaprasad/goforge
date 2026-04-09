"""Tests for remote git URL validation (SSRF guards)."""

import socket
from unittest import TestCase
from unittest.mock import patch

from goforge.repo.remote_clone import (
    _DEFAULT_ALLOWED,
    _select_clone_token,
    build_authenticated_git_url,
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


class TestAuthenticatedGitUrl(TestCase):
    def test_github_uses_x_access_token_scheme(self) -> None:
        u = build_authenticated_git_url(
            "https://github.com/acme/widget",
            "ghp_testtoken",
        )
        self.assertTrue(u.startswith("https://"))
        self.assertIn("x-access-token:", u)
        self.assertIn("github.com/acme/widget", u)

    def test_gitlab_uses_oauth2(self) -> None:
        u = build_authenticated_git_url(
            "https://gitlab.com/group/proj",
            "glpat-xx",
        )
        self.assertIn("oauth2:", u)
        self.assertIn("gitlab.com/group/proj", u)


class TestSelectCloneToken(TestCase):
    def test_prefers_remote_clone_token(self) -> None:
        self.assertEqual(
            _select_clone_token(
                "gitlab.com",
                clone_token="pat-a",
                github_token="pat-b",
            ),
            "pat-a",
        )

    def test_github_falls_back_to_github_token(self) -> None:
        self.assertEqual(
            _select_clone_token(
                "github.com",
                clone_token=None,
                github_token="ghp_x",
            ),
            "ghp_x",
        )

    def test_gitlab_does_not_use_github_token(self) -> None:
        self.assertIsNone(
            _select_clone_token(
                "gitlab.com",
                clone_token=None,
                github_token="ghp_x",
            ),
        )
