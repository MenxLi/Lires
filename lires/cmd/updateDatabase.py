"""
This script is used to update database if data storage format has been change
"""

def stripDataTags():
    """
    Changed on 0.8.0,
    remove whitespace in tags.
    Not work after 1.1.2
    """
    from lires.version import VERSION; assert VERSION < "0.12.0" and VERSION >= "0.8.0"
    from lires.core.dataClass import DataBase, DataPoint
    from lires.confReader import getConf

    db = DataBase()
    db.init(getConf()["database"], force_offline=True)

    for d in db.values():
        if d.fm.getVersionModify() < "0.8.0":
            d.changeTags(d.tags)

def useSqliteStorage(old_db_dir: str) -> str:
    """
    Changed on 0.12.0,
    use sqlite3 to store data.
    Not work after 1.1.2
    """
    import os, json, shutil, tqdm
    from lires.version import VERSION; assert VERSION >= "0.12.0"
    from lires.confReader import getConf
    from lires.core._fileTools_old import FileManipulator as FM_old

    from lires.core.fileTools import FileManipulator as FM_new
    from lires.core.fileTools import addDocument, DBConnection, DocInfo

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

def changeHomeStructure():
    """
    Changed on 1.0.0,
    change home naming
    Not work after 1.1.2
    """
    from lires.version import VERSION; assert VERSION >= "1.0.0"
    from lires.confReader import TMP_DIR, INDEX_DIR, LRS_HOME, getConf
    from lires.server import LRS_SERVER_HOME
    import os, shutil

    home = LRS_HOME
    database_path = getConf()['database']

    old_db = os.path.join(database_path, "rbm.db")
    new_db = os.path.join(database_path, "lrs.db")
    if os.path.exists(old_db):
        shutil.move(old_db, new_db)

    old_db_trash = os.path.join(database_path, ".trash", "rbm.db")
    new_db_trash = os.path.join(database_path, ".trash", "lrs.db")
    if os.path.exists(old_db_trash):
        shutil.move(old_db_trash, new_db_trash)

    old_tmp_dir = os.path.join(home, "RBM.cache")
    old_index_dir = os.path.join(old_tmp_dir, "index")
    if os.path.exists(old_index_dir):
        if os.path.exists(INDEX_DIR):
            shutil.rmtree(INDEX_DIR)
        shutil.move(old_index_dir, INDEX_DIR)

    old_tmp_dir = os.path.join(home, "RBM.cache")
    new_tmp_dir = os.path.join(home, TMP_DIR)
    if os.path.exists(old_tmp_dir):
        if os.path.exists(new_tmp_dir):
            shutil.rmtree(new_tmp_dir)
        shutil.move(old_tmp_dir, new_tmp_dir)

    old_web_dir = os.path.join(home, "RBMWeb")
    if os.path.exists(old_web_dir):
        if os.path.exists(LRS_SERVER_HOME):
            assert os.listdir(os.path.join(LRS_SERVER_HOME, "account")) == [], "account dir is not empty"
            shutil.rmtree(LRS_SERVER_HOME)
        shutil.move(old_web_dir, LRS_SERVER_HOME)
    return


if __name__ == "__main__":
    from lires.confReader import LRS_HOME
    import sys
    print("Running script on $LRS_HOME={}".format(LRS_HOME))

    y = input("It is suggested to backup database before running this stript, continue? (y/[else]): ")
    if y!="y":
        print("Abort.")
        exit()

    # print("stripping datatags")
    # stripDataTags()
    # new_db_dir = useSqliteStorage(sys.argv[1])
    # print(f"new database directory: {new_db_dir}")
    # print("done")

    print("changing home structure")
    changeHomeStructure()
