"""
Miscellaneous handlers,
some small handlers that are not worth putting in a separate file
"""

from ._base import *
from lires import VERSION
from lires_server.types import ServerStatus
import string
import json, time, os

class ReloadDBHandler(RequestHandlerBase):
    @keyRequired
    async def post(self):
        await self.logger.warning("Reload database is deprecated.")
        self.write("OK")

class StatusHandler(RequestHandlerBase):

    _init_time = time.time()

    async def _respond(self):
        self.set_header("Content-Type", "application/json")
        db = await self.db()
        status: ServerStatus = {
            "status": "online",
            "version": VERSION,
            "uptime": time.time() - self._init_time,
            "n_data": await db.count(),
            "n_connections": len(self.connection_pool)
        }
        self.write(json.dumps(status))

    @keyRequired
    async def get(self):
        await self._respond()
    
    @keyRequired
    async def post(self):
        await self._respond()

_api_mainfile_template = string.Template(f"""
// Lires-API v$VERSION (Accessed: $TIME at $URL)
// Run this script with Node.js
// Set `NODE_TLS_REJECT_UNAUTHORIZED=0` to ignore SSL error

import {{ ServerConn }} from "./api.js";

const context = {{
    endpoint: "$URL",
    key: "$KEY"
}}
const conn = new ServerConn(()=>context.endpoint, ()=>context.key)
console.log(await conn.status()) 
""")
class APIGetHandler(RequestHandlerBase):
    @keyRequired
    async def get(self):
        from lires_web import LRSWEB_APIFILE_ROOT
        api_file = os.path.join(LRSWEB_APIFILE_ROOT, "api.js")
        api_d_ts = os.path.join(LRSWEB_APIFILE_ROOT, "api", "serverConn.d.ts")
        protocol_d_ts = os.path.join(LRSWEB_APIFILE_ROOT, "api", "protocol.d.ts")

        example_content = _api_mainfile_template.safe_substitute(
            TIME=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            VERSION=VERSION,
            URL=self.request.protocol + "://" + self.request.host,
            KEY=(await self.userInfo())['enc_key']
        )

        # bundle to zip
        import zipfile
        import io
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as z:
            z.write(api_file, "lib/api.js")
            z.write(api_d_ts, "lib/api.d.ts")
            z.write(protocol_d_ts, "lib/protocol.d.ts")
            z.writestr("main.mjs", example_content)
        zip_buffer.seek(0)
        self.set_header("Content-Type", "application/zip")
        self.set_header("Content-Disposition", "attachment; filename=api.zip")
        self.write(zip_buffer.read())
            