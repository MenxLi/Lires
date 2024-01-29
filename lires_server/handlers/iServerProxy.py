
from ._base import *
import json, sys, math


class IServerProxyHandler(RequestHandlerBase):

    CACHE_TEXT_FEATURE: list[tuple[str, list[float]]] = []
    @keyRequired
    async def post(self, key):
        self.set_header("Content-Type", "application/json")

        if key == "textFeature":
            text = self.get_argument("text")
            require_cache = self.get_argument('require_cache', None) == 'true'

            await self.logger.debug("textFeature request - " + ("cached" if require_cache else "not cached"))
            if require_cache:
                for _cache in self.CACHE_TEXT_FEATURE:
                    if _cache[0] == text:
                        self.write(json.dumps(_cache[1]))
                        return

            ret: list[float] = await self.iconn.featurize(text)

            if require_cache:
                # add the result to the cache buffer
                self.CACHE_TEXT_FEATURE.append((text, ret))
                if sys.getsizeof(self.CACHE_TEXT_FEATURE) > 1e7:
                    # remove the oldest cache if the buffer is larger than 10MB
                    __n_to_remove = min(math.ceil(len(self.CACHE_TEXT_FEATURE) / 2), 100)
                    self.CACHE_TEXT_FEATURE = self.CACHE_TEXT_FEATURE[__n_to_remove:]

            self.write(json.dumps(ret))
        
        else:
            raise tornado.web.HTTPError(404, "Unknown key")

