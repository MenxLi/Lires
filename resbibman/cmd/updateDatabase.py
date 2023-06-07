"""
This script is used to update database if data storage format has been change
"""

def stripDataTags():
    """
    Changed on 0.8.0,
    remove whitespace in tags
    """
    from resbibman.version import VERSION; assert VERSION < "0.12.0" and VERSION >= "0.8.0"
    from resbibman.core.dataClass import DataBase, DataPoint
    from resbibman.confReader import getConf

    db = DataBase()
    db.init(getConf()["database"], force_offline=True)

    for d in db.values():
        if d.fm.getVersionModify() < "0.8.0":
            d.changeTags(d.tags)

def useSqliteStorage(old_db_dir: str) -> str:
    """
    Changed on 0.12.0,
    use sqlite3 to store data
    """
    import os, json, shutil, tqdm
    from resbibman.version import VERSION; assert VERSION >= "0.12.0"
    from resbibman.confReader import getConf
    from resbibman.core._fileTools_old import FileManipulator as FM_old

    from resbibman.core.fileTools import FileManipulator as FM_new
    from resbibman.core.fileTools import addDocument, DBConnection, DocInfo

    new_db_dir = getConf()["database"]
    # make sure new database directory exists and is empty
    if not os.path.exists(new_db_dir):
        os.mkdir(new_db_dir)
    else:
        assert os.listdir(new_db_dir) == [], "new database directory is not empty"

    db_conn = DBConnection(new_db_dir)

    for d in tqdm.tqdm(os.listdir(old_db_dir)):
        dir_path = os.path.join(old_db_dir, d)
        if not os.path.isdir(dir_path):
            print(f"skip {d}")
            continue

        fm_old = FM_old(dir_path)
        _s = fm_old.screen()
        if not _s:
            print(f"skip {d}, not pass data integrity check")
            continue
            
        old_info_file = fm_old.info_p
        with open(old_info_file, "r") as fp:
            old_info = json.load(fp)
        
        # some manual fix...
        if "device_modifky" in old_info:
            old_info["device_modify"] = old_info.pop("device_modifky")
        if not "url" in old_info:
            old_info["url"] = ""

        old_info = DocInfo(**old_info)

        uid = addDocument(
            db_conn, fm_old.readBib(), 
            comments=fm_old.readComments(), 
            doc_src=fm_old.file_p, 
            doc_info=old_info
            )
        # move misc dir
        assert uid is not None, "uid is None"
        fm_new = FM_new(uid, db_conn)

        # check if old misc dir contains files
        old_misc_dir = fm_old.folder_p
        if os.path.exists(old_misc_dir) and os.listdir(old_misc_dir) != []:
            shutil.copytree(old_misc_dir, fm_new.getMiscDir())
    return new_db_dir


if __name__ == "__main__":
    from resbibman.confReader import RBM_HOME
    print("Running script on $RBMHOME={}".format(RBM_HOME))
    y = input("It is suggested to backup database before running this stript, continue? (y/[else]): ")
    if y!="y":
        print("Abort.")
        exit()

    # print("stripping datatags")
    # stripDataTags()
    import sys
    new_db_dir = useSqliteStorage(sys.argv[1])
    print(f"new database directory: {new_db_dir}")
    print("done")
