
from ._base import *
import json
from lires.api.ai import IServerConn

Feat3DT = dict[str, list[float]] | None
class DataFeatureTSNEHandler(RequestHandlerBase):
    """
    Query information of all 3d features
    """
    # TODO: may make a cache to avoid frequent dim reduce
    feat_3d_all: list[tuple[int, Feat3DT]] = []

    @keyRequired
    async def get(self, collection_name: str):
        n_components = self.get_argument("n_components", default="3")
        perplexity = self.get_argument("perplexity", default="-1")
        random_state = self.get_argument("random_state", default="100")

        try:
            vector_collection = self.vec_db.getCollection(collection_name)
        except KeyError:
            raise tornado.web.HTTPError(405, f"Collection {collection_name} not found")
        
        _all_ids = vector_collection.keys()
        all_feat = vector_collection.getBlock(_all_ids)
        if len(all_feat) < 5:
            return self.write(json.dumps({}))

        _feature_signature = hash(str(all_feat) + str(n_components) + str(random_state) + str(perplexity))
        for _old_signature, val in self.__class__.feat_3d_all:
            if _old_signature==_feature_signature:
                await self.logger.debug("Use cached feature.")
                return self.write(json.dumps(val))

        iconn = IServerConn()
        if int(perplexity) < 1:
            await self.logger.debug(f'Perplexity set to {perplexity}, using PCA instead of TSNE')
            all_feat_tsne = await iconn.pca(
                data=all_feat,
                n_components=int(n_components),
                random_state=int(random_state),
            )
        else:
            await self.logger.debug(f'Running TSNE with n_components={n_components}, perplexity={perplexity}, random_state={random_state}')
            all_feat_tsne = await iconn.tsne(
                data=all_feat,
                n_components=int(n_components),
                perplexity=int(perplexity),
                random_state=int(random_state),
                n_iter=5000,
            )

        feat_dict:Feat3DT = {}
        for i, uid in enumerate(_all_ids):
            feat_dict[uid] = all_feat_tsne[i]

        self.__class__.feat_3d_all.append((_feature_signature, feat_dict))
        if len(self.__class__.feat_3d_all)>3:
            self.__class__.feat_3d_all.pop(0)
        self.write(json.dumps(feat_dict))
    
