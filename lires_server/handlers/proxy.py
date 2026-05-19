from ._base import *
import tornado.httpclient
import urllib.parse


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_ALLOWED_QUERY_PARAMS = {
    "search_query",
    "id_list",
    "start",
    "max_results",
    "sortBy",
    "sortOrder",
}


def build_arxiv_proxy_url(raw_query: str) -> str:
    parsed_query = urllib.parse.parse_qs(raw_query, keep_blank_values=False)
    filtered_query = {
        key: values
        for key, values in parsed_query.items()
        if key in ARXIV_ALLOWED_QUERY_PARAMS
    }
    if not filtered_query:
        raise tornado.web.HTTPError(400, "Missing arXiv query parameters")

    return f"{ARXIV_API_URL}?{urllib.parse.urlencode(filtered_query, doseq=True)}"


class ArxivProxyHandler(RequestHandlerBase):
    @authenticate()
    async def get(self):
        url = build_arxiv_proxy_url(self.request.query)
        
        await self.logger.debug(f"ArxivProxyHandler: Proxying to {url}")
        
        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            request = tornado.httpclient.HTTPRequest(
                url=url,
                method="GET",
                headers={
                    "Accept": "application/atom+xml, application/xml;q=0.9, text/xml;q=0.8",
                    "User-Agent": "Lires arXiv proxy/1.0",
                },
                request_timeout=20,
                connect_timeout=10,
            )
            response = await http_client.fetch(request, raise_error=False)
            self.set_status(response.code)
            self.set_header("Content-Type", response.headers.get("Content-Type", "application/xml"))
            self.write(response.body)
            if response.code >= 400:
                await self.logger.error(
                    f"ArxivProxyHandler: Upstream Error {response.code} {response.reason}"
                )
        except tornado.httpclient.HTTPError as e:
            await self.logger.error(f"ArxivProxyHandler: HTTP Error {e.code} {e.message}")
            raise tornado.web.HTTPError(e.code, str(e))
        except Exception as e:
            await self.logger.error(f"ArxivProxyHandler: Error {e}")
            raise tornado.web.HTTPError(500, str(e))
