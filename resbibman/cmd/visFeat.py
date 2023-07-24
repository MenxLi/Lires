"""
Command line tool to visualize the features of the documents in the database.
"""
from resbibman.confReader import DOC_FEATURE_PATH, getConf, TMP_DIR
from resbibman.api import DataBase
import torch
from typing import TypedDict
import os

from sklearn.manifold import TSNE
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Toolbar
from bokeh.embed import components
from bokeh.resources import CDN

class FeatDictItemWthTSNE(TypedDict):
    uid: str
    feature: torch.Tensor
    hash: str
    tsne: torch.Tensor
    desc: str

feat_dict: dict[str, FeatDictItemWthTSNE] = torch.load(DOC_FEATURE_PATH)

all_feat = torch.stack([feat_dict[uid]["feature"] for uid in feat_dict]).numpy()
print("all_feat: ", all_feat.shape)

tsne = TSNE(n_components=2, random_state=100, init="pca", perplexity=30)
all_feat_tsne = tsne.fit_transform(all_feat)
print("all_feat_tsne: ", all_feat_tsne.shape)

for i, uid in enumerate(feat_dict):
    feat_dict[uid]["uid"] = uid
    feat_dict[uid]["tsne"] = all_feat_tsne[i]

print("Loading database...")
db = DataBase(getConf()["database"], force_offline=True)

print("Cleaning data")
# Remove the feature that is not in the database
for uid in list(feat_dict.keys()):
    if uid not in db:
        del feat_dict[uid]
for i, uid in enumerate(feat_dict.keys()):
    feat_dict[uid]["desc"] = str(db[uid])

# Visualize with html
print("Visualizing...")

# Convert your data to a ColumnDataSource
print("Converting data to ColumnDataSource...")
feat_list: FeatDictItemWthTSNE = list(feat_dict.values())
source = ColumnDataSource(data=dict(
    x = [i["tsne"][0] for i in feat_list],
    y = [i["tsne"][1] for i in feat_list],
    id = [i["uid"] for i in feat_list],
    desc = [i["desc"] for i in feat_list],
))

print("Creating figure...")
# Define your tools
hover = HoverTool(tooltips=[
    # ("index", "$index"),
    ("(x,y)", "($x, $y)"),
    ("id", "@id"),
    ("desc", "@desc")
])

# Create a new figure
# tools = [hover, 'pan', 'wheel_zoom', 'reset']
# p = figure(tools=tools, logo=None)

# Create instances of the tools
# pan = PanTool()
# wheel_zoom = WheelZoomTool()
# box_zoom = BoxZoomTool()
# reset = ResetTool()
# Create a new toolbar with the tools and logo set to None
toolbar = Toolbar(tools=[hover], logo=None)

# Create a new figure with the custom toolbar
p = figure(toolbar=toolbar, width=800, height=800, title="Feature Visualization")

# Add a circle renderer with vectorized colors and sizes
p.circle('x', 'y', source=source, size=10)

# Generate the components of the plot
script, div = components(p)

# Create an HTML file
html = f"""
<html>
    <head>
        <title>Visualization</title>
        {CDN.render()}
    </head>
    <body style="display: flex; justify-content: center; align-item: center">
        {div}
        {script}
    </body>
</html>
"""

# Write the HTML file
out_file = os.path.join(TMP_DIR, "hover_glyph.html")
with open(out_file, 'w') as f:
    f.write(html)
print("Output written to: ", out_file)