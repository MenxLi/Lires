from ._base import *
from lires.version import VERSION
import lires

import os, string, time

_js_api_mainfile_template = string.Template(f"""
// Lires-API v$VERSION (Accessed: $TIME at $URL)
import {{ ServerConn }} from "./lib/api.js";

const context = {{
    endpoint: "$URL",
    token: "$KEY"
}};
const conn = new ServerConn(()=>context.endpoint, ()=>context.token);
console.log(await conn.status());
""")
_js_readme_template = string.Template(f"""
# Lires-API v$VERSION
Run the `main.mjs` script with Node.js
Set `NODE_TLS_REJECT_UNAUTHORIZED=0` to ignore SSL error
""")
class APIGetHandler_JS(RequestHandlerBase):
    @keyRequired
    async def get(self):
        from lires_web import LRSWEB_APIFILE_ROOT
        api_file = os.path.join(LRSWEB_APIFILE_ROOT, "api.js")
        api_d_ts = os.path.join(LRSWEB_APIFILE_ROOT, "api", "serverConn.d.ts")
        protocol_d_ts = os.path.join(LRSWEB_APIFILE_ROOT, "api", "protocol.d.ts")

        example_content = _js_api_mainfile_template.safe_substitute(
            TIME=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            VERSION=VERSION,
            URL=self.request.protocol + "://" + self.request.host,
            KEY=(await self.userInfo())['enc_key']
        )

        readme_content = _js_readme_template.safe_substitute(
            VERSION=VERSION
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
            z.writestr("README.md", readme_content)
        zip_buffer.seek(0)
        self.set_header("Content-Type", "application/zip")
        self.set_header("Content-Disposition", "attachment; filename=api.zip")
        self.write(zip_buffer.read())

_py_api_mainfile_template = string.Template(f"""
# Lires-API v$VERSION (Accessed: $TIME at $URL)
# Install the dependencies with `pip install Lires`, 
# or install the latest version with 
# `pip install git+https://github.com/MenxLi/Lires.git`
#
# For more information, visit $URL/documentation/manual/api.html#python

import asyncio
from lires.api import ServerConn

async def main():
    conn = ServerConn(
        endpoint = "$URL",
        token = "$KEY"
    )
    status = await conn.status()
    print(status)

if __name__ == "__main__":
    asyncio.run(main())
""")
            
class APIGetHandler_Py(RequestHandlerBase):
    @keyRequired
    async def get(self):
        example_content = _py_api_mainfile_template.safe_substitute(
            TIME=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            VERSION=VERSION,
            URL=self.request.protocol + "://" + self.request.host,
            KEY=(await self.userInfo())['enc_key']
        )
        self.set_header("Content-Type", "text/plain")
        self.set_header("Content-Disposition", "attachment; filename=main.py")
        self.write(example_content)