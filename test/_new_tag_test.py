
from resbibman.GUIs.tagSelector import TagDataModel

item = TagDataModel.TagDataItem("my->good->daddy")
print(item.allParentTags())

item = TagDataModel.TagDataItem("my")
print(item.allParentTags())

item = TagDataModel.TagDataItem(" ny-> dood")
print(item.allParentTags())