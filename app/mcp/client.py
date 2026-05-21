import httpx
from app.utils.logger import logger


class PulseDeskClient:
    def __init__(self, base_url: str, email: str, password: str):
        self.email = email
        self.password = password
        self._token: str | None = None
        # Persistent HTTP client with base URL and timeout
        self._http = httpx.Client(base_url=base_url, timeout=10.0)

    def _login(self) -> None:
        response = self._http.post(
            "/api/v1/auth/login",
            json={"email": self.email, "password": self.password},
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]
        logger.info("mcp_client_logged_in", email=self.email)

    def _get_token(self) -> str:
        if not self._token:
            self._login()
        return self._token

    def _request(self, method: str, path: str, **kwargs) -> dict:
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        response = self._http.request(method, path, headers=headers, **kwargs)

        if response.status_code == 401:
            # Token expired — re-login and retry once
            logger.info("mcp_client_token_expired_retrying")
            self._token = None
            headers = {"Authorization": f"Bearer {self._get_token()}"}
            response = self._http.request(method, path, headers=headers, **kwargs)

        response.raise_for_status()
        return response.json()

    def search_tickets(
        self,
        status: str | None = None,
        priority: str | None = None,
        page: int = 1,
    ) -> dict:
        params = {"page": page}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        return self._request("GET", "/api/v1/tickets", params=params)

    def get_ticket(self, ticket_id: int) -> dict:
        return self._request("GET", f"/api/v1/tickets/{ticket_id}")
