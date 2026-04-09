"""Create a GitHub pull request after a successful local commit + push."""

from __future__ import annotations

import re
from urllib.parse import quote

import httpx

from goforge.config import settings
from goforge.repo.workspace import (
    git_branch_delete,
    git_checkout,
    git_checkout_new_branch,
    git_commit_all,
    git_push_url,
    git_reset_clean,
    git_resolve_default_branch,
    git_rev_parse_branch,
)


def _parse_owner_repo(value: str) -> tuple[str, str] | None:
    s = value.strip()
    m = re.match(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$", s)
    if not m:
        return None
    return m.group(1), m.group(2)


async def create_pull_request(
    owner: str,
    repo: str,
    token: str,
    *,
    title: str,
    head: str,
    base: str,
    body: str,
) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"title": title, "head": head, "base": base, "body": body}
    timeout = httpx.Timeout(120.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code >= 400:
            detail = response.text[:2000]
            raise RuntimeError(f"GitHub API {response.status_code}: {detail}")
        data = response.json()
    html_url = data.get("html_url")
    if not isinstance(html_url, str):
        raise RuntimeError(f"GitHub API: unexpected response: {data!r}")
    return html_url


async def try_create_github_pr(
    *,
    repo_root: str,
    run_id: str,
    task: str,
) -> tuple[str | None, list[str]]:
    """
    Commit applied changes on a new branch, push to GitHub, open a PR, then
    return to the default branch and delete the local feature branch.

    Returns (pr_url_or_none, log_lines). Does not raise — failures are logged.
    """
    token = settings.github_token
    raw_repo = settings.github_repo
    if not token or not str(token).strip():
        return None, ["PR: skipped — GOFORGE_GITHUB_TOKEN not set."]
    if not raw_repo or not str(raw_repo).strip():
        return None, ["PR: skipped — GOFORGE_GITHUB_REPO not set (owner/name)."]

    parsed = _parse_owner_repo(str(raw_repo))
    if parsed is None:
        return None, [
            f"PR: skipped — invalid GOFORGE_GITHUB_REPO (expected owner/name): {raw_repo!r}"
        ]

    owner, repo_name = parsed
    if settings.github_default_branch.strip():
        base = settings.github_default_branch.strip()
    else:
        base = await git_resolve_default_branch(repo_root)

    head_branch = f"goforge-{run_id.replace('-', '')[:12]}"
    logs: list[str] = [f"PR: using base branch {base!r} (GitHub)."]

    start_branch = await git_rev_parse_branch(repo_root)
    try:
        code, out = await git_checkout_new_branch(repo_root, head_branch)
        if code != 0:
            return None, [f"PR: git checkout -b failed:\n{out}"]

        msg = f"feat(goforge): {task[:60]}"
        code, out = await git_commit_all(repo_root, msg)
        if code != 0:
            return None, [f"PR: git commit failed:\n{out}"]

        safe_tok = quote(str(token).strip(), safe="")
        push_remote = (
            f"https://x-access-token:{safe_tok}@github.com/{owner}/{repo_name}.git"
        )
        refspec = f"HEAD:refs/heads/{head_branch}"
        code, out = await git_push_url(repo_root, push_remote, refspec)
        if code != 0:
            return None, [f"PR: git push failed:\n{out}"]
        logs.append("PR: pushed branch to GitHub.")

        title = f"GoForage: {task[:100]}"
        body = (
            f"Automated by **GoForge** (GoForage).\n\n"
            f"- Run ID: `{run_id}`\n"
        )
        try:
            pr_url = await create_pull_request(
                owner,
                repo_name,
                str(token).strip(),
                title=title,
                head=head_branch,
                base=base,
                body=body,
            )
        except Exception as exc:
            return None, logs + [f"PR: GitHub API error: {exc}"]

        logs.append(f"PR: opened {pr_url}")
        return pr_url, logs
    finally:
        await git_reset_clean(repo_root)
        co, co_out = await git_checkout(repo_root, start_branch)
        if co != 0:
            logs.append(f"PR: warning — git checkout {start_branch!r} failed: {co_out}")
        bd, bd_out = await git_branch_delete(repo_root, head_branch, force=True)
        if bd != 0 and "not found" not in bd_out.lower():
            logs.append(f"PR: warning — branch cleanup: {bd_out}")
