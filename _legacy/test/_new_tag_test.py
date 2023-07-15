
from resbibman.gui.tagSelector import TagDataModel
from resbibman.core.dataClass import TagRule

t = "a->b->c"
t_pool = [
    t,
    "a->b->c->d",
    "a->b->c->",
    "a->b",
    "a",
]

x = TagRule.allChildsOf(t, t_pool)
print(x)