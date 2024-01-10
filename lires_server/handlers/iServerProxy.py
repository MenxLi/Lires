
from ._base import *
import json, sys, math
from lires.api import IServerConn


class IServerProxyHandler(RequestHandlerBase):

    # @minResponseInterval(1e-2)
    CACHE_TEXT_FEATURE: list[tuple[str, list[float]]] = []
    @keyRequired
    async def post(self, key):

        if key == "textFeature":
            text = self.get_argument("text")
            require_cache = self.get_argument('require_cache', None) == 'true'

            self.logger.debug("textFeature request - " + ("cached" if require_cache else "not cached"))
            if require_cache:
                for _cache in self.CACHE_TEXT_FEATURE:
                    if _cache[0] == text:
                        self.write(json.dumps(_cache[1]))
                        return

            ret: list[float] | None = await self.offloadTask(IServerConn().featurize, text)
            if ret is None:
                raise tornado.web.HTTPError(500, "iServer error")

            if require_cache:
                # add the result to the cache buffer
                self.CACHE_TEXT_FEATURE.append((text, ret))
                if sys.getsizeof(self.CACHE_TEXT_FEATURE) > 1e7:
                    # remove the oldest cache if the buffer is larger than 10MB
                    __n_to_remove = min(math.ceil(len(self.CACHE_TEXT_FEATURE) / 2), 100)
                    self.CACHE_TEXT_FEATURE = self.CACHE_TEXT_FEATURE[__n_to_remove:]

            self.write(json.dumps(ret))
            return
        
        else:
            raise tornado.web.HTTPError(404, "Unknown key")

