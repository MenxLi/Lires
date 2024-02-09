"""
The tools that deals with files in the database
"""
from __future__ import annotations
import os, shutil
from typing import List, TypedDict, Optional, TYPE_CHECKING, Any
import aiofiles

from .base import G, LiresBase
from .dbConn import DBConnection, DocInfo
from .bibReader import BibParser, parseBibtex
from ..config import ACCEPTED_EXTENSIONS

if TYPE_CHECKING:
    from .dataTags import DataTags

def _getFileExt(fpath: str):
    """
    Get document extension from file path
    """
    assert not os.path.isdir(fpath)
    ext = os.path.splitext(fpath)[1]
    if ext == "":
        raise ValueError("fpath must have extension")
    if not ext.startswith("."):
        ext = "." + ext
    return ext

async def _addDocumentFileBlob(db_conn: DBConnection, uid: str, file_blob: bytes, ext: str):
    """
    Create document in database directory
    """
    assert ext.startswith(".")
    dst = os.path.join(db_conn.db_dir, uid + ext)
    # with open(dst, "wb") as f:
    #     f.write(file_blob)
    async with aiofiles.open(dst, "wb") as f:
        await f.write(file_blob)
    await db_conn.setDocExt(uid, ext)

async def _addDocumentFile(db_conn: DBConnection, uid: str, src: str):
    """
    Copy document to database directory
    """
    ext = _getFileExt(src)
    async with aiofiles.open(src, "rb") as f:
        await _addDocumentFileBlob(db_conn, uid, await f.read(), ext)

async def addDocument(
        db_conn: DBConnection, 
        citation: str, abstract: str = "", 
        tags: list[str] = [],
        url: str = "",
        comments: str = "", 
        doc_src: Optional[str] = None,
        doc_info: Optional[DocInfo | dict[str, Any]] = None,
        check_duplicate: bool = True
        ) -> Optional[str]:
    """
    Should use this function to add document to database instead of directly using DBConnection.addEntry or use FileGenerator

    - citation: bibtex string, should be valid, at least contains title, year, authors
        may support other formats in the future...
    - doc_src: document source path, should be a file path, if None, doc_ext will be empty, else the document will be copied to the database directory
    - doc_info: DocInfo object, should be None for new data generated, can be provided for data imported from other sources (e.g. old version)
        or, a dict that contains partial information of DocInfo
    - check_duplicate: if True, will check if there is duplicate entry in the database, if there is, will not add the document
    return uuid if success, None if failed
    """
    import pybtex.scanner
    parser = BibParser(mode = "single")
    try:
        bib = (await parser(citation))[0]   # check if citation is valid
    except IndexError as e:
        await G.loggers.core.warning(f"IndexError while parsing bibtex, check if your bibtex info is empty: {e}")
        return 
    except pybtex.scanner.PrematureEOF:
        await G.loggers.core.warning(f"PrematureEOF while parsing bibtex, invalid bibtex")
        return 
    except KeyError:
        await G.loggers.core.warning(f"KeyError. (Author year and title must be provided)")
        return 

    if "abstract" in bib and abstract == "":
        abstract = bib["abstract"][0]
    
    # maybe remove abstract from citation, so that the bibtex won't be too long
    # the abstract will be stored in the database separately
    citation = BibParser.removeAbstract(citation)

    uniform_bib = await parseBibtex(citation)

    if check_duplicate:
        # check if duplicate
        def getSearchStr(bib: dict[str, Any]) -> str:
            return f"title:{bib['title'].lower()} AND year:{bib['year']}"
        search_str = getSearchStr(bib)
        # traverse all entries in the database and check if there is duplicate
        for _uid in await db_conn.keys():
            d_file_info = await db_conn.get(_uid)
            assert d_file_info is not None  # type checking purpose
            aim_bib = (await parser(d_file_info["bibtex"]))[0]
            aim_search_str = getSearchStr(aim_bib)
            if search_str == aim_search_str:
                await G.loggers.core.warning(f"Duplicate entry found: {_uid}")
                return None

    uid = await db_conn.addEntry(
        bibtex=citation,
        title=uniform_bib["title"],
        year=uniform_bib["year"],
        authors=uniform_bib["authors"],
        publication=uniform_bib["publication"] if uniform_bib["publication"] else "",
        tags=tags,
        url=url,
        abstract=abstract,
        comments=comments,
        doc_info=doc_info,
    )

    if uid is None:
        return None     # failed to add entry because of existing uuid

    # copy document
    if doc_src is not None:
        await _addDocumentFile(db_conn, uid, doc_src)
    return uid
    

class FileManipulator(LiresBase):
    logger = LiresBase.loggers().core

    @staticmethod
    async def getDatabaseConnection(db_dir: str) -> DBConnection:
        return await DBConnection(db_dir).init()

    def __init__(self, uid: str):
        self._uid = uid

    async def init(self, db_local: DBConnection) -> FileManipulator:
        self._conn = db_local
        if not await db_local.isInitialized():
            await db_local.init()
        return self

    @property
    def conn(self) -> DBConnection:
        return self._conn
    
    @property
    def uuid(self) -> str:
        return self._uid
    
    async def fileExt(self) -> str:
        """Document file extension, empty string if not exists"""
        d_info = await self.conn.get(self.uuid)
        assert d_info is not None, "uuid {} not exists".format(self.uuid)
        return d_info["doc_ext"]
    
    async def filePath(self) -> Optional[str]:
        """Document file path, None if not exists"""
        file_ext = await self.fileExt()
        if file_ext == "":
            return None
        file_path = os.path.join(self.conn.db_dir, self.uuid + file_ext)
        if not os.path.exists(file_path):
            await self.logger.error("file {} not exists, but file extension exists".format(file_path))
            await self.conn.setDocExt(self.uuid, "")
            await self.logger.warning("cleared the file extension to auto-fix the problem")
            return None
        return file_path

    async def hasFile(self):
        return (await self.filePath()) is not None

    ValidFileT = TypedDict("ValidFileT", {"root": str, "fname": List[str]})
    async def gatherFiles(self) -> ValidFileT:
        """
        gather all files associated with this datapoint,
        may include: document and misc files
        could be used to compress files for upload and download
        """
        # get selected files
        selected_files = []
        if await self.hasFile():
            selected_files.append(await self.filePath())
        if self.hasMisc():
            selected_files.append(self.getMiscDir())
        for f in selected_files:
            assert (os.path.exists(f) and self.conn.db_dir in f), "File {} not in db_dir {}".format(f, self.conn.db_dir)
        selected_fname = [os.path.basename(f) for f in selected_files]
        return {
            "root": self.conn.db_dir,
            "fname": selected_fname,
        }
    
    # miscelaneous files directory
    @property
    def _misc_dir(self):
        return os.path.join(self.conn.db_dir, self.uuid)
    def getMiscDir(self, create = False):
        if create and not os.path.exists(self._misc_dir):
            os.mkdir(self._misc_dir)
        return self._misc_dir
    def hasMisc(self) -> bool:
        if not os.path.exists(self._misc_dir):
            return False
        elif os.path.isdir(self._misc_dir) and os.listdir(self._misc_dir)==[]:
            return False
        else:
            return True
    
    async def addFile(self, extern_file_p) -> bool:
        """
        add file to the database, will copy the file to the database directory
        """
        doc_ext = _getFileExt(extern_file_p)
        if await self.hasFile():
            await self.logger.warning("The file is already existing")
            return False
        if doc_ext not in ACCEPTED_EXTENSIONS:
            await self.logger.warning("The file extension is not supported")
            return False
        with open(extern_file_p, "rb") as f:
            file_blob = f.read()
        return await self.__addRawFileBlob(file_blob, doc_ext)
    
    async def addFileBlob(self, file_blob: bytes, ext: str) -> bool:
        """
        add binary file to the database, will create the file in the database directory
        """
        if await self.hasFile():
            await self.logger.warning("The file is already existing")
            return False
        if ext not in ACCEPTED_EXTENSIONS:
            await self.logger.warning("The file extension is not supported")
            return False
        return await self.__addRawFileBlob(file_blob, ext)
    
    async def __addRawFileBlob(self, file_blob: bytes, ext: str) -> bool:
        """
        add binary file to the database, without condition check
        """
        await _addDocumentFileBlob(self.conn, self.uuid, file_blob, ext)
        await self.logger.debug("(fm) __addRawFileBlob: {}".format(self.uuid))
        return True

    async def getDocSize(self) -> float:
        if not await self.hasFile():
            return 0.0
            # return None
        _f_path = await self.filePath()
        assert _f_path is not None
        size = os.path.getsize(_f_path)
        size = size/(1048576)   # byte to M
        return round(size, 2)

    async def readBib(self) -> str:
        db_data = await self.conn.get(self.uuid); assert db_data
        return db_data["bibtex"]

    async def writeBib(self, bib: str):
        await self.logger.debug("(fm) writeBib: {}".format(self.uuid))
        parsed_bib = await parseBibtex(bib)
        return await self.conn.updateBibtex(
            self.uuid, bib,
            title=parsed_bib["title"],
            authors=parsed_bib["authors"],
            year=parsed_bib["year"],
            publication=parsed_bib["publication"]
            )
    
    async def readAbstract(self) -> str:
        db_data = await self.conn.get(self.uuid); assert db_data
        return db_data["abstract"]
    
    async def writeAbstract(self, abstract: str):
        await self.logger.debug("(fm) writeAbstract: {}".format(self.uuid))
        return await self.conn.updateAbstract(self.uuid, abstract)
    
    async def readComments(self) -> str:
        db_data = await self.conn.get(self.uuid); assert db_data
        return db_data["comments"]
    
    async def writeComments(self, comments: str):
        await self.logger.debug("(fm) writeComments: {}".format(self.uuid))
        await self.conn.updateComments(self.uuid, comments)
    
    async def getTags(self) -> list[str]:
        assert (data:=await self.conn.get(self.uuid)) is not None
        return data["tags"]
    
    async def writeTags(self, tags: list[str] | DataTags):
        await self.logger.debug("(fm) writeTags: {}".format(self.uuid))
        if not isinstance(tags, list):
            tags = tags.toOrderedList()
        await self.conn.updateTags(self.uuid, tags)
    
    async def getWebUrl(self) -> str:
        assert (data:=await self.conn.get(self.uuid)) is not None
        return data["url"]
    
    async def setWebUrl(self, url: str):
        await self.logger.debug("(fm) setWebUrl: {}".format(self.uuid))
        await self.conn.updateUrl(self.uuid, url)
    
    async def getTimeAdded(self) -> float:
        assert (data:=await self.conn.get(self.uuid)) is not None
        return data["time_import"]
    
    async def getTimeModified(self) -> float:
        assert (data:=await self.conn.get(self.uuid)) is not None
        return data["time_modify"]
    
    async def deleteEntry(self, create_backup = True) -> bool:
        """
        Will delete the entry from the database, and delete the file and misc folder if exist.
        if create_backup is True, will create a backup of the document
        """
        if create_backup:
            _conn_dir = self.conn.db_dir
            _backup_dir = os.path.join(_conn_dir, ".trash")
            if not os.path.exists(_backup_dir):
                os.mkdir(_backup_dir)
            old_entry = await self.conn.get(self.uuid)
            assert old_entry
            async with (await DBConnection(_backup_dir).init()) as trash_db:
                _success = await trash_db.addEntry(
                    bibtex=old_entry["bibtex"],
                    title=old_entry["title"],
                    year=old_entry["year"],
                    authors=old_entry["authors"],
                    publication=old_entry["publication"],
                    tags=old_entry["tags"],
                    url=old_entry["url"],
                    abstract=old_entry["abstract"],
                    comments=old_entry["comments"],
                    doc_info=DocInfo.fromString(old_entry["info_str"]),
                    )
                if _success:    # otherwise, maybe duplicate entry
                    if await self.hasFile():
                        await _addDocumentFile(trash_db, self.uuid, await self.filePath())  # type: ignore
                    if self.hasMisc():
                        shutil.copytree(self._misc_dir, os.path.join(_backup_dir, self.uuid))
            await self.logger.debug("(fm) deleteEntry: {} (backup created)".format(self.uuid))
        
        if await self.hasFile():
            await self.deleteDocument()
        if os.path.exists(self._misc_dir):
            shutil.rmtree(self._misc_dir)
        return await self.conn.removeEntry(self.uuid)
    
    async def deleteDocument(self) -> bool:
        if not await self.hasFile():
            return False
        file_p = await self.filePath(); assert file_p is not None
        os.remove(file_p)
        await self.conn.setDocExt(self.uuid, "")
        await self.logger.debug("(fm) deleteDocument: {}".format(self.uuid))
        return True
