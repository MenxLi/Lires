"""
Command line tool to visualize the features of the documents in the database.
"""
from resbibman.confReader import DOC_FEATURE_PATH, getConf, TMP_DIR
from resbibman.api import DataBase
import torch
from typing import TypedDict
import os

from sklearn.manifold import TSNE 
from sklearn.cluster import SpectralClustering

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.offline as pyo


class FeatDictItemWthTSNE(TypedDict):
    uid: str
    feature: torch.Tensor
    hash: str
    tsne: torch.Tensor
    desc: str
    cluster_label: int

print("Loading database...")
db = DataBase(getConf()["database"], force_offline=True)
feat_dict: dict[str, FeatDictItemWthTSNE] = torch.load(DOC_FEATURE_PATH)

all_feat: np.ndarray = torch.stack([feat_dict[uid]["feature"] for uid in feat_dict]).numpy()
print("all_feat: ", all_feat.shape)

# tsne = TSNE(n_components=2, random_state=100, init="pca", perplexity=30)
tsne = TSNE(n_components=3, random_state=100, perplexity=10)
all_feat_tsne = tsne.fit_transform(all_feat)

N_CLUSTER = len([t for t in db.total_tags if t[0].isalpha()])
if len(all_feat) < N_CLUSTER:
    N_CLUSTER = len(all_feat)

print("Clustering...")
# clustering = KMeans(
#     n_clusters=N_CLUSTER,
#     n_init="auto",
#     ).fit(all_feat)
clustering = SpectralClustering(
    n_clusters=N_CLUSTER,
    n_jobs=-1,
).fit(all_feat)
labels = clustering.labels_
print("Total number of clusters: ", np.unique(labels).shape[0])

for i, uid in enumerate(feat_dict):
    feat_dict[uid]["uid"] = uid
    feat_dict[uid]["tsne"] = all_feat_tsne[i]
    feat_dict[uid]["cluster_label"] = labels[i]


print("Cleaning data")
# Remove the feature that is not in the database
for uid in list(feat_dict.keys()):
    if uid not in db:
        del feat_dict[uid]
for i, uid in enumerate(feat_dict.keys()):
    feat_dict[uid]["desc"] = str(db[uid])

## Vis
# Prepare data for Plotly
uids = list(feat_dict.keys())
feat_list = np.array([feat_dict[uid]["tsne"] for uid in uids])
data = pd.DataFrame({
    'x': feat_list[:, 0],
    'y': feat_list[:, 1],
    'z': feat_list[:, 2],
    'uid': uids,
    'short_desc': [db[uid].getAuthorsAbbr() for uid in uids],
    'desc': [feat_dict[uid]["desc"] for uid in uids],
    'tags': [", ".join(db[uid].tags.toOrderedList()) for uid in uids],
    'cluster_label': [feat_dict[uid]["cluster_label"] for uid in uids],
})

# Create a 3D scatter plot with Plotly
fig = px.scatter_3d(data, x='x', y='y', z='z', hover_data=['uid', 'desc'], color='cluster_label', color_continuous_scale='Viridis')
fig.update_traces(marker=dict(size=6))

# Save the interactive plot to an HTML file using offline mode
out_file = os.path.join(TMP_DIR, "hover_glyph_3d.html")
pyo.plot(fig, filename=out_file, auto_open=False)
print("Saved to: ", out_file)

# plot_html = fig.to_html(full_html=False)
# print(plot_html)