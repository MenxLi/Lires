
from ._base import *
from sklearn.manifold import TSNE 
import numpy as np
import json
from lires.core.utils import Timer

Feat3DT = dict[str, list[float]] | None
class DataFeatureTSNEHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """
    Query information of all 3d features
    """
    # TODO: may make a cache to avoid frequent dim reduce
    # feat_3d_all: dict[str, Feat3DT] = {}

    @keyRequired
    async def get(self, collection_name: str):
        self.setDefaultHeader()

        n_components = self.get_argument("n_components", default="3")
        perplexity = self.get_argument("perplexity", default="10")
        random_state = self.get_argument("random_state", default="100")

        try:
            vector_collection = self.vec_db.getCollection(collection_name)
        except KeyError:
            raise tornado.web.HTTPError(405, f"Collection {collection_name} not found")
        
        _all_ids = vector_collection.keys()
        _all_feat = vector_collection.getBlock(_all_ids)
        all_feat = np.array(_all_feat)

        def runTSNE():
            with Timer("TSNE", print_func=self.logger.debug):
                all_feat_tsne = TSNE(
                    n_components=int(n_components), 
                    random_state=int(random_state), 
                    perplexity=int(perplexity), 
                    n_jobs=None,
                    ).fit_transform(all_feat).astype(np.float16)
                # normalize along each dimension
                # n_dim = all_feat_tsne.shape[1]
                # for i in range(n_dim):
                #     all_feat_tsne[:,i] = (all_feat_tsne[:,i] - all_feat_tsne[:,i].min()) / (all_feat_tsne[:,i].max() - all_feat_tsne[:,i].min())
            return all_feat_tsne.tolist()

        all_feat_tsne = await self.offloadTask(runTSNE)

        feat_dict:Feat3DT = {}
        for i, uid in enumerate(_all_ids):
            feat_dict[uid] = all_feat_tsne[i]
        
        self.write(json.dumps(feat_dict))
    
