import dataclasses

import asyncio
from lires.loader import DatabasePool
from lires.user import UserPool
from lires.api import IServerConn

@dataclasses.dataclass(frozen=True)
class GlobalStorage:
    """Global storage for all handlers"""
    database_pool: DatabasePool
    user_pool: UserPool
    iconn: IServerConn

    async def flush(self):
        """
        Commit and flush all changes to disk
        """
        await asyncio.gather(
            self.database_pool.commit(),
            self.user_pool.commit()
        )
    
    async def finalize(self):
        """
        Finalize the storage
        """
        await self.flush()
        await asyncio.gather(
            self.database_pool.close(),
            self.user_pool.close()
        )
        