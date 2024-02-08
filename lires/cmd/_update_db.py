
# temp script to update database structure, in 1.4.x -> 1.5.x

import os, shutil, tqdm, asyncio
from lires.utils import TimeUtils
from lires.core.dbConn import DBConnection, DocInfo
from lires.core.bibReader import parseBibtex
from lires.core.dbConn_ import DBConnection as DBConnection_old
from lires.core.dbConn_ import DocInfo as DocInfo_old
from lires.config import TMP_DIR, DATABASE_DIR

async def sync(conn: DBConnection, conn_old: DBConnection_old):
    await conn.init()
    await conn_old.init()

    all_uids = await conn_old.keys()
    all_entries = await conn_old.getMany(all_uids)

    for old_entry in tqdm.tqdm(all_entries):
        bib = await parseBibtex(old_entry["bibtex"])
        old_info = DocInfo_old.fromString(old_entry["info_str"])
        new_info = DocInfo(
            uuid = old_info.uuid,
            version_import=old_info.version_import,
            version_modify=old_info.version_modify,
            device_import=old_info.device_import,
            device_modify=old_info.device_modify,
        )
        
        uid = await conn.addEntry(
            bibtex = old_entry["bibtex"],
            title = bib["title"],
            year = bib["year"],
            publication = bib["publication"],
            authors = bib["authors"],

            tags = old_info.tags,
            url = old_info.url,
            abstract = old_entry["abstract"],
            comments= old_entry["comments"],
            doc_ext= old_entry["doc_ext"],
            doc_info= new_info,
        )
        assert uid == old_info.uuid

        # update time_import
        time_import = old_info.time_import
        if isinstance(time_import, str):
            # backward compatibility, < 0.6.0
            time_import = TimeUtils.strLocalTimeToDatetime(time_import).timestamp()
        
        await conn.conn.execute(
            """
            UPDATE files SET time_import = ? WHERE uuid = ?
            """, (time_import, uid)
            )
    await conn.commit()

    # remove transh dir
    trash_dir = os.path.join(conn.db_dir, ".trash")
    if os.path.exists(trash_dir):
        shutil.rmtree(trash_dir)
    
    print("Done")

if __name__ == "__main__":
    temp_backup = os.path.join(TMP_DIR, "DB_BACKUP_1.4.x_to_1.5.x-{}".format(TimeUtils.nowStamp()))
    # make a backup of the old database
    if os.path.exists(temp_backup):
        exit("Backup already exists, please remove it first: {}".format(temp_backup))
    
    print("Backup old database to {}".format(temp_backup))
    shutil.copytree(DATABASE_DIR, temp_backup)

    conn_old = DBConnection_old(temp_backup)
    conn = DBConnection(DATABASE_DIR)

    # remove the old database in DATABASE_DIR
    if os.path.exists(conn.db_path):
        os.remove(conn.db_path)

    asyncio.run(sync(conn, conn_old))

    
