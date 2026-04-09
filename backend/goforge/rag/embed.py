"""OpenAI-compatible embeddings API (batch)."""

from __future__ import annotations

from typing import Any

import httpx

from goforge.config import settings


async def embed_texts(texts: list[str], *, model: str | None = None) -> list[list[float]]:
    """
    Return one embedding vector per input string (same order).
    Uses GOFORGE_OPENAI_API_KEY and GOFORGE_OPENAI_BASE_URL.
    """
    if not texts:
        return []

    key = settings.openai_api_key
    if not key or not str(key).strip():
        raise ValueError("openai_api_key required for embeddings")

    m = model or settings.openai_embedding_model
    url = f"{settings.openai_base_url.rstrip('/')}/embeddings"
    headers = {
        "Authorization": f"Bearer {key.strip()}",
        "Content-Type": "application/json",
    }

    # API accepts batch; split to keep payloads reasonable.
    batch_size = 32
    all_vecs: list[list[float]] = []
    timeout = httpx.Timeout(120.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            body: dict[str, Any] = {"model": m, "input": batch}
            response = await client.post(url, headers=headers, json=body)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = response.text[:1200]
                raise RuntimeError(
                    f"embeddings HTTP {response.status_code}: {detail}"
                ) from exc

            payload = response.json()
            data = payload.get("data")
            if not isinstance(data, list) or len(data) != len(batch):
                raise RuntimeError(f"embeddings: unexpected response shape: {payload!r}")

            # Sort by index in case API reorders
            indexed: list[tuple[int, list[float]]] = []
            for item in data:
                idx = item.get("index")
                emb = item.get("embedding")
                if not isinstance(emb, list) or idx is None:
                    raise RuntimeError(f"embeddings: bad item: {item!r}")
                indexed.append((int(idx), [float(x) for x in emb]))
            indexed.sort(key=lambda x: x[0])
            for _, vec in indexed:
                all_vecs.append(vec)

    return all_vecs


async def embed_query(text: str, *, model: str | None = None) -> list[float]:
    vecs = await embed_texts([text], model=model)
    return vecs[0]
