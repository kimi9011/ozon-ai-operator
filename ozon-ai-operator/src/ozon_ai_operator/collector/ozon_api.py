from __future__ import annotations
import os, time, requests

class OzonAPI:
    """Thin configurable Ozon Seller API client.

    Endpoint methods are intentionally explicit/configurable because Ozon may change
    API versions and account availability. No secret is stored in source control.
    """
    def __init__(self, client_id: str | None = None, api_key: str | None = None, base_url: str | None = None):
        self.client_id = client_id or os.getenv("OZON_CLIENT_ID")
        self.api_key = api_key or os.getenv("OZON_API_KEY")
        self.base_url = (base_url or os.getenv("OZON_API_BASE", "https://api-seller.ozon.ru")).rstrip("/")
        if not self.client_id or not self.api_key:
            raise RuntimeError("Missing OZON_CLIENT_ID/OZON_API_KEY")
        self.session = requests.Session()
        self.session.headers.update({"Client-Id": self.client_id, "Api-Key": self.api_key, "Content-Type": "application/json"})

    def post(self, path: str, payload: dict, retries: int = 3) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        for attempt in range(retries):
            r = self.session.post(url, json=payload, timeout=60)
            if r.status_code < 400:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Ozon API {r.status_code}: {r.text[:500]}")
        return {}

    def call_configured(self, env_var: str, payload: dict) -> dict:
        path = os.getenv(env_var)
        if not path:
            raise RuntimeError(f"Set {env_var} to an endpoint path from your current Ozon Seller API documentation")
        return self.post(path, payload)
