
from ._base import *
from sklearn.manifold import TSNE 
from sklearn.decomposition import PCA
import numpy as np
import json
from lires.utils import Timer

Feat3DT = dict[str, list[float]] | None
class DataFeatureTSNEHandler(RequestHandlerBase):
    """
    Query information of all 3d features
    """
    # TODO: may make a cache to avoid frequent dim reduce
    feat_3d_all: list[tuple[int, Feat3DT]] = []

    @keyRequired
    async def get(self, collection_name: str):
        self.allowCORS()

        n_components = self.get_argument("n_components", default="3")
        perplexity = self.get_argument("perplexity", default="-1")
        random_state = self.get_argument("random_state", default="100")

        try:
            vector_collection = self.vec_db.getCollection(collection_name)
        except KeyError:
            raise tornado.web.HTTPError(405, f"Collection {collection_name} not found")
        
        _all_ids = vector_collection.keys()
        _all_feat = vector_collection.getBlock(_all_ids)
        all_feat = np.array(_all_feat)
        if len(all_feat) < 5:
            return self.write(json.dumps({}))

        def _runTSNE(perplexity: int):
            with Timer("TSNE", print_func=self.logger.debug):
                self.logger.debug(f'Running TSNE with n_components={n_components}, perplexity={perplexity}, random_state={random_state}')
                all_feat_tsne = TSNE(
                    n_components=int(n_components), 
                    random_state=int(random_state), 
                    perplexity=perplexity, 
                    n_jobs=None,
                    n_iter=5000,
                    ).fit_transform(all_feat).astype(np.float16)
            return all_feat_tsne
        
        def _runPCA():
            with Timer("PCA", print_func=self.logger.debug):
                self.logger.debug(f'Running PCA with n_components={n_components}, random_state={random_state}')
                all_feat_tsne = PCA(
                    n_components=int(n_components), 
                    random_state=int(random_state), 
                    ).fit_transform(all_feat).astype(np.float16)
            return all_feat_tsne

        _feature_signature = hash(str(all_feat.tolist()) + str(n_components) + str(random_state) + str(perplexity))
        for _old_signature, val in self.__class__.feat_3d_all:
            if _old_signature==_feature_signature:
                self.logger.debug("Use cached feature.")
                return self.write(json.dumps(val))

        if int(perplexity) < 1:
            self.logger.debug(f'Perplexity set to {perplexity}, using PCA instead of TSNE')
            all_feat_tsne: np.ndarray = await self.offloadTask(_runPCA)
        else:
            all_feat_tsne: np.ndarray = await self.offloadTask(_runTSNE, int(perplexity))

        # normalize along each dimension
        # n_dim = all_feat_tsne.shape[1]
        # for i in range(n_dim):
        #     all_feat_tsne[:,i] = (all_feat_tsne[:,i] - all_feat_tsne[:,i].min()) / (all_feat_tsne[:,i].max() - all_feat_tsne[:,i].min()) - 0.5

        all_feat_tsne = all_feat_tsne.tolist()
        feat_dict:Feat3DT = {}
        for i, uid in enumerate(_all_ids):
            feat_dict[uid] = all_feat_tsne[i]
        

        self.__class__.feat_3d_all.append((_feature_signature, feat_dict))
        if len(self.__class__.feat_3d_all)>3:
            self.__class__.feat_3d_all.pop(0)
        self.write(json.dumps(feat_dict))
    
