from RBMWeb.backend.discussUtils import DiscussDatabase, DiscussSet
db = DiscussDatabase()

dset = DiscussSet(db, "file-xxa")
dset.addDiscuss("monsoon", "asdfasdf", "Good")
s = db.discussions("file-xxx")
print(s)

db.delDiscuss("6df54406-10c6-4e49-b055-787b2598d3ee")
db.delDiscussAll("file-xxx")

print(db["asdfasdf"])
print(db["14376454-f7f7-485a-a442-48c0dea105c9"])
