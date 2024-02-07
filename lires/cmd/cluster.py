"""
Server clustering script.
It reads a toml config file and starts the servers.
"""

from lires.version import VERSION
from lires.config import LRS_HOME
from lires.utils import BCOLORS
from typing import TypedDict
import os, argparse, subprocess, signal, time
import tomlkit

class ConfigEntryT(TypedDict, total=False):
    ENVS: dict
    ARGS: dict

class ClusterConfigT(TypedDict):
    GLOBAL_ENVS: dict
    server: list[ConfigEntryT]
    ai: list[ConfigEntryT]
    log: list[ConfigEntryT]
allowed_entries = ["GLOBAL_ENVS", "server", "ai", "log"]
exec_entries = allowed_entries[1:]

def __getDefaultConfig()->ClusterConfigT:
    ssl_certfile = os.environ.get("LRS_SSL_CERTFILE", "")
    ssl_keyfile = os.environ.get("LRS_SSL_KEYFILE", "")
    return {
        "GLOBAL_ENVS": {
            "LRS_HOME": LRS_HOME,
            # disable logging to terminal, as it will be messy if the log server are also running
            "LRS_TERM_LOG_LEVEL": "CRITICAL",   
        },
        "server": [
            {
                "ENVS": {
                    "LRS_HOME": LRS_HOME,
                    "LRS_SSL_CERTFILE": ssl_certfile,
                    "LRS_SSL_KEYFILE": ssl_keyfile,
                },
                "ARGS": {
                    "--port": 8080,
                },
            }
        ],
        "log": [{}],
        "ai": [
            {
                "ENVS": {
                    "OPENAI_API_KEY": "sk-xxxxx",
                    "OPENAI_API_BASE": "https://api.openai.com/v1",
                    "HF_ENDPOINT": "https://hf-mirror.com",
                },
                "ARGS": {
                    "--local-llm-chat": "",
                    "--openai-models": ["gpt-3.5-turbo", "gpt-4"],
                },
            }
        ],
    }

def generateConfigFile(path:str):
    config = __getDefaultConfig()
    with open(path, "w") as f:
        tomlkit.dump(config, f)
    
    comments = [
        "This is config file for lires cluster - version {}".format(VERSION),
        "It serves as a script for starting multiple servers with different configurations",
        "The GLOBAL_ENV variables are set globally, and can be overridden by the entries",
        "Each entry is marked by a ...--- Entry ---... for better readability",
        "The entry names are the subcommands for `lires`",
        "Please refer to the `lires -h` for more information on the subcommands",
    ]
    # inject comments onto the top of the file
    with open(path, "r") as f:
        content_lines = f.readlines()
    # new_content = "# " + "\n# ".join(comments) + "\n\n" + content
    __entry_line_nums = []
    for i in range(len(content_lines)):
        if content_lines[i].strip().startswith("[["):
            __entry_line_nums.append(i)
    for i in __entry_line_nums[::-1]:
        content_lines.insert(i, "\n# ----------- Entry -------------\n")
    content_lines.insert(0, "\n# " + "\n# ".join(comments) + "\n\n")
            
    with open(path, "w") as f:
        f.writelines(content_lines)

def loadConfigFile(path:str)->ClusterConfigT:
    with open(path, "r") as f:
        config: ClusterConfigT = tomlkit.parse(f.read()) # type: ignore
    
    ## Validate config...
    if not isinstance(config, dict):
        raise ValueError("Config file must be a dict")
    if not isinstance(config["GLOBAL_ENVS"], dict):
        raise ValueError("GLOBAL_ENVS must be a dict")
    for k in config.keys():
        assert k in allowed_entries, \
            "Config file keys must be in : GLOBAL_ENVS, server, ai, log"
    # check if service entries are valid
    for k in exec_entries:
        if k not in config:
            config[k] = []
        if not isinstance(config[k], list):
            raise ValueError(f"{k} must be a list")
        
        for i, item in enumerate(config[k]):
            if not isinstance(item, dict):
                raise ValueError(f"{k}[{i}] must be a dict")
            if "ENVS" not in item:
                item["ENVS"] = dict()
            if not isinstance(item["ENVS"], dict):
                raise ValueError(f"{k}[{i}].ENVS must be a dict")
            if "ARGS" not in item:
                item["ARGS"] = dict()
            if not isinstance(item["ARGS"], dict):
                raise ValueError(f"{k}[{i}].ARGS must be a dict")
        
        for entry in config[k]:
            for __key in entry:
                assert __key in ["ENVS", "ARGS"], \
                    "Config entry keys must be in : ENVS, ARGS"

    return config


def cprint(*args):
    """ Custom print function """
    print(BCOLORS.LIGHTMAGENTA + "[cluster] " + " ".join(map(str, args)) + BCOLORS.ENDC)

## Multi-processes
def initProcesses(config: ClusterConfigT):
    """ Execute the config file """
    ps: list[subprocess.Popen] = []
    g_environ = os.environ.copy()

    def __parseEnv(env:dict, dst: dict):
        for k, v in env.items():
            if v is None:
                if k in dst:
                    del dst[k]
            else:
                dst[k] = v
    def __execEntry(subcommand: str, entry: ConfigEntryT):
        this_environ = g_environ.copy()
        assert "ENVS" in entry, "Config entry must have ENVS"
        assert "ARGS" in entry, "Config entry must have ARGS"
        __parseEnv(entry["ENVS"], this_environ)
        exec_args = ["lires", subcommand]
        for k, v in entry["ARGS"].items():
            if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
                exec_args.append(f"{k}")
                exec_args.append(str(v))
            elif isinstance(v, list):
                exec_args.append(k)
                for item in v:
                    exec_args.append(str(item))
            else:
                raise ValueError(f"Invalid value type for {k}: {type(v)}")
        
        # print the command
        cprint(f"{' '.join(exec_args)}")

        ps.append(
            subprocess.Popen(
                exec_args,
                env = this_environ,
                start_new_session=True,     # a new session makes the process independent from the parent, thus we can control it with SIGINT
            )
        )
    
    __parseEnv(config["GLOBAL_ENVS"], g_environ)
    for key in exec_entries:
        for entry in config[key]:
            __execEntry(key, entry)
    
    return ps

def main():
    parser = argparse.ArgumentParser(description="Generate config file for lires cluster")
    parser.add_argument("path", type=str, help="path to the config file")
    parser.add_argument("--generate", action="store_true", help="generate init config file, then exit")
    parser.add_argument("--overwrite", action="store_true", help="overwrite existing config file")

    parser.add_argument("-i", "--init-if-not-exist", 
                        action="store_true", help="initialize the config file if it does not exist")
    args = parser.parse_args()

    if args.generate:
        if os.path.exists(args.path) and not args.overwrite:
            cprint("Config file already exists, use --overwrite to overwrite")
            exit(1)
        generateConfigFile(args.path)
        exit(0)
    
    if args.overwrite and not args.generate:
        cprint("--overwrite can only be used with --generate")
        exit(1)
    
    if not os.path.exists(args.path) and args.init_if_not_exist:
        generateConfigFile(args.path)
    
    if not os.path.exists(args.path):
        cprint("Config file does not exist, use --generate to generate one")
        exit(1)
    
    ## Start registry -------------------------------
    cprint("Starting registry...")
    p0 = subprocess.Popen(["lires", "registry"], env=os.environ, start_new_session=True)

    # waiting for it to be functional
    import asyncio, aiohttp.client_exceptions
    from lires.api import RegistryConn
    _rconn = RegistryConn()
    while (True):
        try:
            asyncio.run(_rconn.status())
            break
        except aiohttp.client_exceptions.ClientConnectorError:
            time.sleep(0.1)
    
    ## Start servers -------------------------------
    config = loadConfigFile(args.path)
    procs = initProcesses(config)

    # handle SIGINT
    def sigintHandler(sig, frame):
        print("")   # print a newline
        cprint("{} received, terminating...".format(signal.Signals(sig).name))

        # terminate all processes
        for p in procs:
            p.terminate()
        # wait for all processes to terminate
        for p in procs:
            p.wait()
        
        # lastly, terminate the registry
        p0.terminate()
        p0.wait()

        cprint("All processes terminated, exit.")
        exit(0)

    signal.signal(signal.SIGINT, sigintHandler)
    signal.signal(signal.SIGTERM, sigintHandler)
    
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
