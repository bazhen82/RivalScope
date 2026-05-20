import base64
import logging
import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from backend.config import settings
from backend.models.schemas import ParsedPage


logger = logging.getLogger(__name__)


class ParserService:
    def _normalize_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            return f"https://{url}"
        return url

    def _extract_from_html(
        self, html: str, url: str, screenshot_base64: Optional[str] = None
    ) -> ParsedPage:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()

        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        h1_tag = soup.find("h1")
        h1 = h1_tag.get_text(" ", strip=True) if h1_tag else ""
        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(" ", strip=True)) > 50
        ]
        first_paragraph = paragraphs[0] if paragraphs else ""
        text_excerpt = " ".join(soup.get_text(" ", strip=True).split())[:6000]

        return ParsedPage(
            url=url,
            title=title,
            h1=h1,
            first_paragraph=first_paragraph,
            text_excerpt=text_excerpt,
            screenshot_base64=screenshot_base64,
        )

    async def parse_http(self, url: str) -> ParsedPage:
        normalized = self._normalize_url(url)
        logger.info("HTTP parsing started: %s", normalized)
        async with httpx.AsyncClient(
            timeout=settings.parser_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 RivalScope/1.0"},
        ) as client:
            response = await client.get(normalized)
            response.raise_for_status()
        return self._extract_from_html(response.text, str(response.url))

    async def parse_selenium(self, url: str) -> ParsedPage:
        normalized = self._normalize_url(url)
        logger.info("Selenium parsing started: %s", normalized)
        options = Options()
        if settings.selenium_headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1440,1200")
        options.add_argument("--lang=ru-RU")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
        try:
            driver.set_page_load_timeout(settings.parser_timeout_seconds)
            driver.get(normalized)
            time.sleep(3)
            html = driver.page_source
            screenshot_base64 = base64.b64encode(driver.get_screenshot_as_png()).decode(
                "utf-8"
            )
            return self._extract_from_html(html, driver.current_url, screenshot_base64)
        finally:
            driver.quit()

    async def parse(self, url: str, use_selenium: bool = True) -> ParsedPage:
        if use_selenium:
            try:
                return await self.parse_selenium(url)
            except Exception as exc:
                logger.exception("Selenium parsing failed, falling back to HTTP: %s", exc)
                return await self.parse_http(url)
        return await self.parse_http(url)


parser_service = ParserService()
