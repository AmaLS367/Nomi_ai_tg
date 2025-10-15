import httpx
from typing import Any, Dict, List, Optional
import logging
import asyncio
import random

log = logging.getLogger(__name__)

class NomiClient:
    def __init__(self, api_key: str, timeout: float = 30.0):
        self._headers = {
            "Authorization": api_key,
            "User-Agent": "NomiTGCompanion/1.0 (+github.com/AmaLS367)"
        }
        self._timeout = httpx.Timeout(timeout, connect=15.0, read=timeout, write=timeout)
        self._base = "https://api.nomi.ai"

    async def _request(self, method: str, url: str, json: Optional[dict] = None) -> httpx.Response:
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=self._timeout, headers=self._headers) as s:
                    r = await s.request(method, url, json=json)
                if r.status_code == 429 and attempt < 2:
                    retry_after = r.headers.get("Retry-After")
                    base = float(retry_after) if (retry_after and retry_after.isdigit()) else 0.8 * (attempt + 1)
                    await asyncio.sleep(base + random.uniform(0, 0.3))
                    continue
                if r.status_code >= 500 and attempt < 2:
                    await asyncio.sleep(0.8 * (attempt + 1) + random.uniform(0, 0.3))
                    continue

                r.raise_for_status()
                return r
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                if attempt == 2:
                    raise
                await asyncio.sleep(0.8 * (attempt + 1))
        raise RuntimeError("unreachable")

    async def list_nomis(self) -> List[Dict[str, Any]]:
        r = await self._request("GET", f"{self._base}/v1/nomis")
        data = r.json()
        if isinstance(data, list):
            return data
        return data.get("nomis", []) if isinstance(data, dict) else []

    def _extract_text(self, data: Any) -> Optional[str]:
        if isinstance(data, dict):
            rm = data.get("replyMessage")
            if isinstance(rm, dict):
                t = rm.get("text")
                if t:
                    return str(t).strip() or None
            m = data.get("message")
            if isinstance(m, dict):
                t = m.get("text") or m.get("content")
                if t:
                    return str(t).strip() or None

        if data is None:
            return None
        if isinstance(data, str):
            return data.strip() or None
        if isinstance(data, dict):
            for k in ("text", "content", "reply", "answer"):
                v = data.get(k)
                t = self._extract_text(v)
                if t:
                    return t
            if "messages" in data and isinstance(data["messages"], list) and data["messages"]:
                for item in reversed(data["messages"]):
                    if isinstance(item, dict) and item.get("role") in ("assistant", "nomi", "ai", "bot"):
                        t = self._extract_text(item)
                        if t:
                            return t
                return self._extract_text(data["messages"][-1])
        if isinstance(data, list) and data:
            return self._extract_text(data[-1])
        return None

    async def chat_direct(self, nomi_id: str, text: str) -> Optional[str]:
        payload = {"messageText": text}
        r = await self._request("POST", f"{self._base}/v1/nomis/{nomi_id}/chat", json=payload)
        raw = r.text
        try:
            data = r.json()
        except Exception:
            log.warning("Non-JSON direct chat response: %s", raw)
            return raw.strip() or None
        return self._extract_text(data)
