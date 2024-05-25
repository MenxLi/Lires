from __future__ import annotations
from lires.core.base import LiresBase
import aiosqlite, asyncio
from typing import TypedDict, Literal, TypeVar, Generic
from .wrap import FixSizeAlg

DB_MOD_LOCK = asyncio.Lock()

class CollectionConfig(TypedDict):
    name: str
    dimension: int
    conent_type: Literal["BLOB", "TEXT"]

ContentT = TypeVar("ContentT", str, bytes)
class VectorEntry(TypedDict):
    uid: str
    vector: list[float]
    group: str
    content: str | bytes

class VectorCollection(LiresBase, Generic[ContentT]):
    logger = LiresBase.loggers().get("vector")

    def __init__(
        self, 
        parent: VectorDatabase,
        config: CollectionConfig
        ) -> None:
        super().__init__()
        self._parent = parent
        self.config = config
        self.alg = FixSizeAlg(config["dimension"])
    
    @property
    def conn(self):
        return self._parent.conn
    
    @property
    def name(self):
        return self.config["name"]
    
    @property
    def dimension(self):
        return self.config["dimension"]

    async def init(self):
        async with DB_MOD_LOCK:
            # mata data
            res = await self.conn.execute(
                f"SELECT * FROM metadata WHERE name = ?", (self.name,)
            )
            row = await res.fetchone()
            if row is not None:
                assert row[1] == self.dimension, "Dimension mismatch"
            else:
                await self.conn.execute(
                    f"INSERT INTO metadata (name, dim) VALUES (?, ?)",
                    (self.name, self.dimension)
                )
                
            # table
            sql = f"CREATE TABLE IF NOT EXISTS {self.config['name']} ("\
                "uid TEXT PRIMARY KEY, "\
                "vector BLOB NOT NULL, "\
                "group_name TEXT DEFAULT '', "\
                f"content {self.config['conent_type']} DEFAULT '')"
            await self.conn.execute(sql)
            await self.commit()
        return self
    
    async def insert(self, entry: VectorEntry):
        vec_enc = self.alg.encode(entry["vector"])
        async with DB_MOD_LOCK:
            await self.conn.execute(
                f"INSERT INTO {self.config['name']} (uid, vector, group_name, content) VALUES (?, ?, ?, ?)",
                (entry["uid"], vec_enc, entry["group"], entry["content"])
            )
    
    async def update(self, entry: VectorEntry):
        vec_enc = self.alg.encode(entry["vector"])
        async with DB_MOD_LOCK:
            await self.conn.execute(
                f"UPDATE {self.config['name']} SET vector = ?, group_name = ?, content = ? WHERE uid = ?",
                (vec_enc, entry["group"], entry["content"], entry["uid"])
            )
    
    async def deleteGroup(self, group: str):
        async with DB_MOD_LOCK:
            await self.conn.execute( f"DELETE FROM {self.config['name']} WHERE group_name = ?", (group,))
    
    async def getGroup(self, group: str) -> list[VectorEntry]:
        res = await self.conn.execute(
            f"SELECT * FROM {self.config['name']} WHERE group_name = ?", (group,)
        )
        rows = await res.fetchall()
        return [
            {
                "uid": row[0],
                "vector": self.alg.decode(row[1]),
                'group': row[2],
                "content": row[3]
            }
            for row in rows
        ]
    
    async def keys(self) -> list[str]:
        async with self.conn.execute(f"SELECT uid FROM {self.config['name']}") as res:
            return [row[0] async for row in res]
    
    async def groups(self) -> list[str]:
        async with self.conn.execute(f"SELECT DISTINCT group_name FROM {self.config['name']}") as res:
            return [row[0] async for row in res]

    async def get(self, uid: str) -> VectorEntry:
        res = await self.conn.execute(
            f"SELECT * FROM {self.config['name']} WHERE uid = ?", (uid,)
        )
        row = await res.fetchone()
        if row is None:
            raise self.Error.LiresEntryNotFoundError(f"vector uid: {uid}")
        return {
            "uid": row[0],
            "vector": self.alg.decode(row[1]),
            "group": row[2], 
            "content": row[3]
        }
    
    async def getMany(self, uids: list[str]) -> list[VectorEntry]:
        return await asyncio.gather(*[self.get(uid) for uid in uids])
    
    async def search(
        self, 
        query: list[float], 
        top_k: int, 
        group: str | None = None,
        type: Literal["cosine", "l2"] = "cosine", 
        ) -> tuple[list[str], list[float]]:
        """return top_k uid"""

        similarity_fn = self.alg.similarity if type == "cosine" else self.alg.l2score

        q_enc = self.alg.encode(query)
        if group is None:
            res = await self.conn.execute( f"SELECT uid, vector FROM {self.config['name']}")
        else:
            res = await self.conn.execute( f"SELECT uid, vector FROM {self.config['name']} WHERE group_name = ?", (group,))
        rows = await res.fetchall()
        counter = 0
        ids = []
        scores = []
        search_buffer: list[bytes] = []
        for row in rows:
            ids.append(row[0])
            search_buffer.append(row[1])

            counter += 1
            if counter == 1024:
                scores += similarity_fn(q_enc, search_buffer)
                search_buffer.clear()
                counter = 0
        if search_buffer:
            scores += similarity_fn(q_enc, search_buffer)
        
        top_k_indices = self.alg.topKIndices(scores, top_k)
        return [ids[i] for i in top_k_indices], [scores[i] for i in top_k_indices]
    
    async def delete(self, uid: str):
        async with DB_MOD_LOCK:
            await self.conn.execute(
                f"DELETE FROM {self.config['name']} WHERE uid = ?", (uid,)
            )
    
    async def clearAll(self):
        async with DB_MOD_LOCK:
            await self.conn.execute( f"DELETE FROM {self.config['name']}")
            await self.conn.execute( f"VACUUM")
    
    async def commit(self):
        await self._parent.commit()
        

class VectorDatabase(LiresBase):
    logger = LiresBase.loggers().get("vector")

    def __init__(self, db_path: str, configs: list[CollectionConfig]):
        super().__init__()
        self.path = db_path
        self.configs = configs
    
    async def init(self):
        async with DB_MOD_LOCK:
            self.conn = await aiosqlite.connect(self.path)
            await self.conn.execute(
                "CREATE TABLE IF NOT EXISTS metadata (name TEXT PRIMARY KEY, dim INTEGER)"
            )
            await self.commit()

        self.collections: dict[str, VectorCollection] = {}
        for config in self.configs:
            self.collections[config["name"]] = VectorCollection(self, config)
            await self.collections[config["name"]].init()
        return self
        
    async def allCollectionNames(self) -> list[str]:
        return list(self.collections.keys())
   
    async def getCollection(self, name: str) -> VectorCollection:
        return self.collections[name]
    
    async def deleteCollection(self, name: str):
        async with DB_MOD_LOCK:
            await self.conn.execute( f"DROP TABLE IF EXISTS {name}")
            await self.conn.execute( f"DELETE FROM metadata WHERE name = ?", (name,))
            await self.commit()
    
    async def commit(self):
        await self.conn.commit()
    
    async def close(self):
        await self.conn.close()


__all__ = ["VectorCollection", "VectorDatabase", "CollectionConfig"]