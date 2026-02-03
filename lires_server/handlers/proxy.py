from ._base import *
import tornado.httpclient
import urllib.parse

class ArxivProxyHandler(RequestHandlerBase):
    @authenticate()
    async def get(self):
        # We only support GET for now as arXiv API uses GET
        
        # Get all arguments
        query = self.request.query
        
        # Construct target URL
        # We need to make sure the query is safely constructed, but here we just forward it.
        # Ideally we should parse and reconstruct to avoid injection if there were sensitive headers, 
        # but for public arxiv API it should be fine.
        
        url = f"https://export.arxiv.org/api/query?{query}"
        
        await self.logger.debug(f"ArxivProxyHandler: Proxying to {url}")
        
        # Use Tornado's AsyncHTTPClient
        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            response = await http_client.fetch(url)
            # Forward relevant headers? Arxiv returns atom+xml usually.
            self.set_header("Content-Type", response.headers.get("Content-Type", "application/xml"))
            self.write(response.body)
        except tornado.httpclient.HTTPError as e:
            await self.logger.error(f"ArxivProxyHandler: HTTP Error {e.code} {e.message}")
            raise tornado.web.HTTPError(e.code, str(e))
        except Exception as e:
            await self.logger.error(f"ArxivProxyHandler: Error {e}")
            raise tornado.web.HTTPError(500, str(e))
