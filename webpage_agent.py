import asyncio
from typing import Dict, List, Any, Optional, Union

from base_agent import BaseAgent
from synthesizer_agent_deep_research import SynthesizerAgentDeepResearch


class WebpageAgent(BaseAgent):
    """
    Agent that fetches webpage content using crawl4ai and forwards it
    to the synthesizer for integration into the final report.

    Usage patterns:
    - run(user_question, url="https://...")
    - run(user_question, urls=["https://...", "https://..."])
    """

    def __init__(self):
        super().__init__("Webpage Agent")
        self.synthesizer_agent = SynthesizerAgentDeepResearch()

    # BaseAgent abstract methods ------------------------------------------------
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Interpret `query` as a URL when provided; otherwise expect `url` or `urls` in kwargs.
        Returns a list of standardized source dicts with `source_type='webpage'`.
        """
        # Prefer explicit kwargs
        url: Optional[str] = kwargs.get("url")
        urls: Optional[List[str]] = kwargs.get("urls")

        # Fallback: treat query as a single URL if it looks like one
        if not url and not urls and isinstance(query, str) and query.startswith(("http://", "https://")):
            url = query

        if url:
            return [self._fetch_one(url)]
        if urls:
            return [self._fetch_one(u) for u in urls if isinstance(u, str) and u.startswith(("http://", "https://"))]

        # Nothing to do
        return []

    def process_sources(self, sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        # Webpage content is already normalized in _fetch_one
        return sources

    # Public API ----------------------------------------------------------------
    def run(self, user_question: str, **kwargs) -> Dict[str, Any]:
        """
        Crawl the provided URL(s) and synthesize with the given user question.

        kwargs:
          - url: str
          - urls: list[str]
        """
        url = kwargs.get("url")
        urls = kwargs.get("urls")

        if not url and not urls:
            raise ValueError("WebpageAgent requires 'url' or 'urls' in kwargs.")

        # Collect sources
        sources = self.search(url or "", url=url, urls=urls)

        if not sources:
            return {
                "agent": self.name,
                "sources": [],
                "result": "No webpage content could be fetched for the provided URL(s).",
            }

        # Synthesize final report using webpage sources
        final_report = self.synthesizer_agent.synthesize(user_question, sources)

        return {
            "agent": self.name,
            "sources": sources,
            "result": final_report,
        }

    # Internal helpers ----------------------------------------------------------
    def _fetch_one(self, url: str) -> Dict[str, Any]:
        """
        Fetch a single URL via crawl4ai and normalize the output into a source dict.
        """
        try:
            from crawl4ai import AsyncWebCrawler  # type: ignore
        except Exception as e:
            return {
                "title": url,
                "content": f"crawl4ai not available: {e}",
                "link": url,
                "source_type": "webpage",
            }

        async def _fetch(url: str):
            async with AsyncWebCrawler() as crawler:
                return await crawler.arun(url=url)

        # Run the coroutine robustly across environments
        try:
            result = asyncio.run(_fetch(url))
        except RuntimeError:
            # Fall back if an event loop is already running (e.g., notebooks)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import threading

                container: Dict[str, Any] = {}

                def runner():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        container["value"] = new_loop.run_until_complete(_fetch(url))
                    finally:
                        new_loop.close()

                t = threading.Thread(target=runner)
                t.start()
                t.join()
                result = container.get("value")
            else:
                result = loop.run_until_complete(_fetch(url))

        # Extract best-available text/markdown
        content = None
        for attr in (
            "markdown_v2",
            "markdown",
            "extracted_text",
            "cleaned_html",
            "html",
            "raw_html",
        ):
            if hasattr(result, attr):
                val = getattr(result, attr)
                if val:
                    content = val
                    break

        # Extract title from metadata when available
        title = None
        meta = getattr(result, "metadata", None)
        if isinstance(meta, dict):
            title = meta.get("title") or meta.get("og:title")
        elif meta is not None:
            # Support objects with attribute-style access
            title = getattr(meta, "title", None) or getattr(meta, "og:title", None)

        if not title:
            title = url
        if not content:
            content = f"No readable content extracted from: {url}"

        return {
            "title": title,
            "content": content,
            "link": url,
            "source_type": "webpage",
        }
