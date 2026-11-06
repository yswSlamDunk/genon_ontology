"""LLM 연결 — OpenAI 방식 주소. 키는 geo-proto/.env(형구님이 set_key.sh로 넣은 것)를 서버가 읽기만 하고 출력하지 않음.

GENO_LLM_OFF=1 이면 LLM을 쓰지 않음(설계 초안은 열 이름 규칙, 문서 읽기 · Copilot 질문은 막힘).
"""
import base64
import json
import os
from pathlib import Path

import httpx

ENV_FILE = Path(os.environ.get("GENO_ENV", Path.home() / "Project/geo-proto/.env"))


def _env() -> dict:
    vals = {k: v for k, v in os.environ.items() if k.startswith("GEO_LLM_")}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                vals.setdefault(k.strip(), v.strip())
    return vals


def available() -> bool:
    if os.environ.get("GENO_LLM_OFF") == "1":
        return False
    return bool(_env().get("GEO_LLM_API_KEY"))


def info() -> dict:
    e = _env()
    return {"available": available(), "model": e.get("GEO_LLM_MODEL", "") if available() else ""}


def _mime(p: Path) -> str:
    return {".png": "image/png", ".webp": "image/webp"}.get(p.suffix.lower(), "image/jpeg")


def embed(texts: list[str], timeout: float = 60) -> list[list[float]]:
    """임베딩(뜻을 숫자 목록으로) — OpenAI 방식 /embeddings. 모델은 GEO_LLM_EMBED_MODEL(없으면 text-embedding-3-small)."""
    if not available():
        raise RuntimeError("LLM 키가 없습니다.")
    e = _env()
    base = e.get("GEO_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    out = []
    for i in range(0, len(texts), 64):
        r = httpx.post(f"{base}/embeddings", headers={"Authorization": f"Bearer {e.get('GEO_LLM_API_KEY', '')}"},
                       json={"model": e.get("GEO_LLM_EMBED_MODEL", "text-embedding-3-small"), "input": texts[i:i + 64]}, timeout=timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"임베딩 호출에 실패했습니다. ({r.status_code})")
        out += [d["embedding"] for d in r.json()["data"]]
    return out


def chat_json(system: str, user: str, image: Path | list | None = None, timeout: float = 120) -> dict:
    if not available():
        raise RuntimeError("LLM 키가 없습니다. geo-proto/.env 파일을 확인해 주세요.")
    """JSON 한 덩어리를 돌려받음. image가 있으면 그림도 같이 보냄(스캔본 읽기)."""
    e = _env()
    base = e.get("GEO_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    content: list | str = user
    if image is not None:
        imgs = image if isinstance(image, list) else [image]
        content = [{"type": "text", "text": user}] + [
            {"type": "image_url", "image_url": {"url": f"data:{_mime(im)};base64,{base64.b64encode(im.read_bytes()).decode()}"}} for im in imgs]
    r = httpx.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {e.get('GEO_LLM_API_KEY', '')}"},
        json={"model": e.get("GEO_LLM_MODEL", "gpt-5.4-mini"),
              "messages": [{"role": "system", "content": system + "\n답은 JSON 객체 하나로만(json)."}, {"role": "user", "content": content}],
              "response_format": {"type": "json_object"}},
        timeout=timeout,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"LLM 호출에 실패했습니다. ({r.status_code}) {r.text[:200]}")
    return json.loads(r.json()["choices"][0]["message"]["content"])
