from typing import Optional, Tuple, List, Dict, Any
from .client import NomiClient

class NomiService:
    def __init__(self, client: NomiClient, default_nomi_id: Optional[str]):
        self.client = client
        self.default_nomi_id = default_nomi_id
        self.default_nomi_name: Optional[str] = None

    async def _resolve_default(self) -> Tuple[str, Optional[str]]:
        nomis: List[Dict[str, Any]] = await self.client.list_nomis()
        if not nomis:
            raise RuntimeError("No Nomi found in your account")
        if self.default_nomi_id:
            for n in nomis:
                if str(n.get("id")) == self.default_nomi_id:
                    return self.default_nomi_id, str(n.get("name") or "")
        n = nomis[0]
        return str(n.get("id")), str(n.get("name") or "")

    async def ensure_default(self) -> Tuple[str, Optional[str]]:
        if not self.default_nomi_id:
            nid, name = await self._resolve_default()
            self.default_nomi_id = nid
            self.default_nomi_name = name
        elif self.default_nomi_name is None:
            _, name = await self._resolve_default()
            self.default_nomi_name = name
        return self.default_nomi_id, self.default_nomi_name

    async def send(self, text: str) -> str:
        nid, _ = await self.ensure_default()
        resp = await self.client.chat_direct(nid, text)
        return resp or "No response"
