"""
Miscellaneous handlers,
some small handlers that are not worth putting in a separate file
"""

from ._base import *
from lires import VERSION
from lires_server.types import ServerStatus
from lires.user import UserInfo
import json, time

class StatusHandler(RequestHandlerBase):

    _init_time = time.time()

    async def _respond(self, user_info: UserInfo):
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        status: ServerStatus = {
            "status": "online",
            "version": VERSION,
            "uptime": time.time() - self._init_time,
            "n_data": await db.count(),
            "n_connections": len(self.connectionsByUserID(user_info["id"])),
            "n_connections_all": len(self.connection_pool),
        }
        self.write(json.dumps(status))

    @authenticate()
    async def get(self):
        await self._respond(await self.userInfo())
    
    @authenticate()
    async def post(self):
        await self._respond(await self.userInfo())

class DatabaseDownloadHandler(RequestHandlerBase):

    __download_request_time = {}
    __global_download_request_time = []

    def checkReqFrequency(self, user_id: int):
        _prev_request_times = self.__download_request_time.get(user_id, [0])
        n_last_req = [t for t in _prev_request_times if time.time() - t < 600]
        if len(n_last_req) >= 3:
            # 3 requests in 10 minutes
            self.set_header("Retry-After", 600)
            raise tornado.web.HTTPError(429, "Too many requests from this user")
        
        _g_prev_request_times = self.__global_download_request_time
        n_last_req = [t for t in _g_prev_request_times if time.time() - t < 6000]
        if len(n_last_req) >= 20:
            # 20 requests in 60 minutes
            self.set_header("Retry-After", 6000)
            raise tornado.web.HTTPError(429, "Too many requests from all users")
        
        # update the request times
        curr_time = time.time()
        
        _prev_request_times.append(curr_time)
        if len(_prev_request_times) > 5:
            _prev_request_times = _prev_request_times[-5:]
        self.__download_request_time[user_id] = _prev_request_times
        
        _g_prev_request_times.append(curr_time)
        if len(_g_prev_request_times) > 100:
            _g_prev_request_times = _g_prev_request_times[-100:]
        self.__global_download_request_time = _g_prev_request_times
    
    @authenticate()
    async def get(self):
        include_data = self.get_argument("data", "false").lower() == "true"

        user_info = await self.userInfo()
        db = await self.db()

        self.checkReqFrequency(user_info["id"])

        if not include_data:
            await self.logger.info(f"User {user_info['username']} is downloading the database")
            self.set_header("Content-Type", "application/octet-stream")
            self.set_header("Content-Disposition", f"attachment; filename=\"{user_info['username']}.lires.sqlite\"")
            self.write(await db.dump(include_files=False))
        else:
            # first check the size
            db_size = await db.diskUsage()
            if db_size > 512*1024*1024:
                self.set_header("Content-Type", "text/html")
                # info = f"Database is too large to be downloaded ({db_size/1024/1024:.1f} M), please use the API to download in parts."
                self.write( """
                <html>
                <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    gap: 10px;
                    height: 100vh;
                    margin: 0;
                    padding: 0;
                    margin-inline: 20px;
                }}

                h2{{
                    margin: 0;
                    padding: 0;
                }}
                
                p {{
                    font-size: 1.2em;
                    max-width: 500px;
                    margin: 0;
                    padding: 0;
                    text-align: center;
                    color: #666;
                }}
                </style>
                <head><title>Database too large</title></head>
                <body>
                <h2>ERROR: Database too large</h2>
                <p>
                Database is too large to be downloaded ({size:.1f} M).
                Please use the API to download in parts, 
                or set the <code>data</code> parameter to <code>false</code> to download without data.
                </p>
                </body>
                </html>
                """.format(size=db_size/1024/1024).replace("\n", ""))
                return
            
            # download the data as zip
            await self.logger.info(f"User {user_info['username']} is downloading the database (data included)")
            self.set_header("Content-Type", "application/zip")
            self.set_header("Content-Disposition", f"attachment; filename=\"{user_info['username']}.lires.zip\"")
            self.write(await db.dump(include_files=True))