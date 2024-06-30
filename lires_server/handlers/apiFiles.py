from ._base import *
from lires.version import VERSION
from lires_server.path_config import ASSETS_DIR

import os, string, time
import zipfile
import io

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
    @authenticate()
    async def get(self):
        js_api_root = os.path.join(ASSETS_DIR, "js-api")
        api_file = os.path.join(js_api_root, "api.js")
        api_d_ts = os.path.join(js_api_root, "api", "serverConn.d.ts")
        protocol_d_ts = os.path.join(js_api_root, "api", "protocol.d.ts")

        example_content = _js_api_mainfile_template.safe_substitute(
            TIME=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            VERSION=VERSION,
            URL=self.request.protocol + "://" + self.request.host,
            KEY=(await self.userInfo())['enc_key']
        )

        readme_content = _js_readme_template.safe_substitute(
            VERSION=VERSION
        )

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
    @authenticate()
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

_obsidian_plugin_readme_template = string.Template(f"""
# Lires-Obsidian-Plugin v$VERSION
This plugin is used to connect obsidian with Lires server
For more information, visit [the manual]($URL/documentation/manual/obsidianPlugin.html)
""")
class ObsidianPluginGetHandler(RequestHandlerBase):
    async def get(self):
        obsidian_plugin_root = os.path.join(ASSETS_DIR, "obsidian-plugin")
        if not os.path.exists(obsidian_plugin_root):
            self.write("Error: Obsidian plugin not built on this server.")
            return

        self.set_header("Content-Type", "application/zip")
        self.set_header("Content-Disposition", "attachment; filename=lires-obsidian-plugin.zip")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as z:
            for root, _, files in os.walk(obsidian_plugin_root):
                for file in files:
                    if file == "data.json":
                        # make sure the data.json is not accidentally leaked
                        continue
                    z.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), obsidian_plugin_root))
            readme_content = _obsidian_plugin_readme_template.safe_substitute(
                VERSION=VERSION,
                URL=self.request.protocol + "://" + self.request.host
            )
            z.writestr("README.md", readme_content)
        zip_buffer.seek(0)
        self.write(zip_buffer.read()) 
