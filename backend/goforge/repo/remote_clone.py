"""Clone or refresh a remote Git repository for PatchFlow runs (HTTPS, allowlisted hosts)."""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import re
import shutil
import socket
import subprocess
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger("goforge.remote_clone")

_DEFAULT_ALLOWED = frozenset(
    {"github.com", "gitlab.com", "bitbucket.org", "codeberg.org"}
)


def _parse_allowed_hosts(raw: str) -> frozenset[str]:
    s = raw.strip()
    if not s:
        return _DEFAULT_ALLOWED
    return frozenset(x.strip().lower() for x in s.split(",") if x.strip())


def _host_allowed(hostname: str, allowed: frozenset[str]) -> bool:
    h = hostname.lower().rstrip(".")
    for a in allowed:
        if h == a or h.endswith("." + a):
            return True
    return False


def _bad_ip(addr: str) -> bool:
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return True
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _dns_safe(hostname: str) -> None:
    try:
        infos = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve host: {hostname!r} ({exc})") from exc
    for info in infos:
        ip_str = info[4][0]
        if _bad_ip(ip_str):
            raise ValueError(
                f"Host {hostname!r} resolves to a disallowed address ({ip_str})."
            )


def validate_remote_git_url(url: str, *, allowed_hosts: frozenset[str]) -> str:
    """
    Validate an HTTPS git remote URL for cloning. Returns normalized URL string.
    Raises ValueError with a short reason on failure.
    """
    raw = url.strip()
    if not raw:
        raise ValueError("Empty repository URL.")
    if len(raw) > 2048:
        raise ValueError("Repository URL is too long.")

    parsed = urlparse(raw)
    if parsed.scheme.lower() != "https":
        raise ValueError("Only https:// repository URLs are allowed.")

    if parsed.username or parsed.password:
        raise ValueError(
            "Credentials in the URL are not allowed; use a public clone URL."
        )

    host = parsed.hostname
    if not host:
        raise ValueError("Repository URL is missing a hostname.")

    if not _host_allowed(host, allowed_hosts):
        raise ValueError(
            f"Host {host!r} is not allowed. Configure GOFORGE_REMOTE_ALLOWED_HOSTS "
            "or use a host such as github.com."
        )

    if parsed.query or parsed.fragment:
        raise ValueError("Repository URL must not include query or fragment characters.")

    path = parsed.path or ""
    if not path or path == "/":
        raise ValueError("Repository URL must include a path (e.g. /owner/repo).")

    if re.search(r"\.(php|asp|jsp|cgi)$", path, re.I):
        raise ValueError("Suspicious repository path.")

    _dns_safe(host)

    return f"https://{host}{path}"


def _run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout_s: float,
) -> None:
    try:
        subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.CalledProcessError as exc:
        err = (exc.stderr or exc.stdout or "").strip()[:2000]
        raise RuntimeError(f"git failed ({exc.returncode}): {err or 'no output'}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git timed out after {timeout_s}s") from exc


def ensure_cached_clone(
    normalized_url: str,
    *,
    cache_root: Path,
    timeout_s: float,
) -> Path:
    """
    Clone or fast-forward update a shallow clone under cache_root.
    Returns the absolute path to the repository root.
    """
    key = hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()[:32]
    repo_dir = (cache_root / key).resolve()
    cache_root.mkdir(parents=True, exist_ok=True)

    if (repo_dir / ".git").is_dir():
        logger.info("Updating cached clone: %s", repo_dir)
        try:
            _run_git(
                ["git", "-C", str(repo_dir), "pull", "--ff-only"],
                timeout_s=timeout_s,
            )
        except RuntimeError:
            logger.warning("git pull failed; recloning into %s", repo_dir)
            shutil.rmtree(repo_dir, ignore_errors=True)

    if not repo_dir.is_dir() or not (repo_dir / ".git").is_dir():
        if repo_dir.exists():
            shutil.rmtree(repo_dir, ignore_errors=True)
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Cloning %s -> %s", normalized_url, repo_dir)
        _run_git(
            ["git", "clone", "--depth", "1", normalized_url, str(repo_dir)],
            timeout_s=timeout_s,
        )

    return repo_dir


def resolve_remote_repo_root(
    repo_url: str,
    *,
    cache_root: Path,
    allowed_hosts_raw: str,
    timeout_s: float,
) -> Path:
    """Validate URL, ensure clone exists, return absolute repo path."""
    allowed = _parse_allowed_hosts(allowed_hosts_raw)
    normalized = validate_remote_git_url(repo_url, allowed_hosts=allowed)
    return ensure_cached_clone(
        normalized,
        cache_root=cache_root,
        timeout_s=timeout_s,
    )
