"""
This script is used to update database if data storage format has been change
"""

def stripDataTags():
    """
    Changed on 0.8.0
    """
    from resbibman.core.dataClass import DataBase, DataPoint
    from resbibman.confReader import getConf

    db = DataBase()
    db.init(getConf()["database"], force_offline=True)

    for d in db.values():
        if d.fm.getVersionModify() < "0.8.0":
            d.changeTags(d.tags)

if __name__ == "__main__":
    from resbibman.confReader import RBM_HOME
    print("Running script on $RBMHOME={}".format(RBM_HOME))
    y = input("It is suggested to backup database before running this stript, continue? (y/[else]): ")
    if y!="y":
        print("Abort.")
        exit()

    print("stripping datatags")
    stripDataTags()
    print("done")