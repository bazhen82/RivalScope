import requests


class RivalScopeClient:
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        return requests.get(f"{self.base_url}/health", timeout=10).json()

    def analyze_text(self, text: str, context: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/analyze_text",
            json={"text": text, "context": context},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def parse_site(self, url: str, context: dict, use_selenium: bool = True) -> dict:
        response = requests.post(
            f"{self.base_url}/parse_demo",
            json={"url": url, "context": context, "use_selenium": use_selenium},
            timeout=180,
        )
        response.raise_for_status()
        return response.json()

    def history(self) -> dict:
        return requests.get(f"{self.base_url}/history", timeout=20).json()
