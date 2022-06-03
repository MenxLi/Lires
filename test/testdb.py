from RBMWeb.backend.discussUtils import DiscussDatabase, DiscussSet
db = DiscussDatabase()

dset = DiscussSet(db, "file-xxx")
dset.addDiscuss("monsoon", "asdfasdf", "Good")
