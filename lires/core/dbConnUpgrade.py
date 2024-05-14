from __future__ import annotations
from typing import TYPE_CHECKING
import re
if TYPE_CHECKING:
    from .dbConn import DBConnection


async def upgrade_1_8_0(db: DBConnection):
    """ 
    Add 'type' column to the database
    """
    _re_dtype = re.compile(r"^\s*@\s*(\w+)\s*{")
    def dtypeFromBibtex(bib: str) -> str:
        m = _re_dtype.match(bib)
        if m is None:
            return ""
        return m.group(1).lower()

    # ensure type column not exists
    async with db.conn.execute("PRAGMA table_info(files)") as cursor:
        cols = await cursor.fetchall()
        for col in cols:
            if col[1] == "type":
                return
    # add type field
    await db.logger.debug("Elevating database to version 1.8.0")

    # create a new table
    await db.conn.execute("""
    CREATE TABLE IF NOT EXISTS
    files_new (
        uuid TEXT PRIMARY KEY,

        bibtex TEXT NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        year INTEGER NOT NULL,
        publication TEXT NOT NULL,
        authors TEXT NOT NULL,

        tags TEXT NOT NULL,
        url TEXT NOT NULL,
        abstract TEXT NOT NULL,
        comments TEXT NOT NULL,
        time_import REAL NOT NULL DEFAULT 0,
        time_modify REAL NOT NULL DEFAULT 0,
        info_str TEXT NOT NULL,
        doc_ext TEXT NOT NULL,
        misc_dir TEXT
    )
    """)
    # copy data
    async with db.conn.execute("SELECT * FROM files") as cursor:
        rows = await cursor.fetchall()
    for row in rows:
        bibtex = row[1]
        dtype = dtypeFromBibtex(bibtex)
        await db.conn.execute(
            """
            INSERT INTO files_new (uuid, bibtex, type, title, year, publication, authors, tags, url, abstract, comments, time_import, time_modify, info_str, doc_ext, misc_dir)
            VALUES (?, ?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?)
            """,
            (row[0], row[1], dtype, *row[2:])
        )
    # drop old table
    await db.conn.execute("DROP TABLE files")
    # rename new table
    await db.conn.execute("ALTER TABLE files_new RENAME TO files")