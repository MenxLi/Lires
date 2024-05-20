"""
Server clustering script.
It reads a yaml config file and starts the servers.
"""

from lires.version import VERSION
from lires.config import LRS_HOME
from lires.utils import BCOLORS, randomAlphaNumeric
from typing import TypedDict
import os, argparse, subprocess, signal, time
import re
import yaml

class _ConfigEntryT(TypedDict, total=False):
    env: dict
    args: list
class ConfigEntryT(_ConfigEntryT):
    name: str

class ClusterConfigT(TypedDict):
    VERSION: str
    GLOBAL_ENV: dict
    ENTRIES: list[ConfigEntryT]

allowed_entries = ['log', 'ai', 'feed', 'server']
exec_order = allowed_entries

def __getDefaultConfig()->ClusterConfigT:
    ssl_certfile = os.environ.get("LRS_SSL_CERTFILE", "")
    ssl_keyfile = os.environ.get("LRS_SSL_KEYFILE", "")
    return {
        "VERSION": "0.1.0",
        "GLOBAL_ENV": {
            "LRS_HOME": LRS_HOME,
            "LRS_KEY": randomAlphaNumeric(32),
            # disable logging to terminal, as it will be messy if the log server are also running
            "LRS_TERM_LOG_LEVEL": "CRITICAL",   
        },
        "ENTRIES": [
            {
                "name": "server",
                "env": {
                    "LRS_SSL_CERTFILE": ssl_certfile,
                    "LRS_SSL_KEYFILE": ssl_keyfile,
                },
                "args": [
                    "--port", 8080,
                ]
            },
            {
                "name": "ai",
                "env": {
                    # "OPENAI_API_KEY": "sk-xxxxx",
                    # "OPENAI_API_BASE": "https://api.openai.com/v1",
                    "HF_ENDPOINT": "https://hf-mirror.com",
                }
            },
            { "name": "log"},
            { "name": "feed"},
        ]
    }

def generateConfigFile(path:str):
    config = __getDefaultConfig()

    # use yaml
    with open(path, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False, indent=2)
    
    comments = [
        "This is config file for lrs-cluster, generated with lires version {}".format(VERSION),
        "It serves as a script for starting multiple servers with different configurations",
        "The GLOBAL_ENV variables are set globally, and can be overridden by the entries",
        "The entry names are the subcommands for `lires`",
        "Please refer to the `lires -h` for more information on the subcommands",
    ]
    # inject comments onto the top of the file

    with open(path, "r") as f:
        content = f.read()

    # add spacing to the top-level keys
    output = []
    reg_exp_l0 = re.compile(r"^(\w+):", re.MULTILINE)
    reg_exp_l1 = re.compile(r"^- name: .*$", re.MULTILINE)
    for line in content.split("\n"):
        if reg_exp_l0.match(line):
            line = "\n# ===============================\n" + line
            # line = "\n" + line
        elif reg_exp_l1.match(line):
            # line = "\n# ------------ ENTRY ------------\n" + line
            # line = "\n# entry ---\n" + line
            line = "\n" + line
        output.append(line)
    content = "\n".join(output)
    
    with open(path, "w") as f:
        f.write("# " + "\n# ".join(comments) + "\n" + content)

def loadConfigFile(path:str)->ClusterConfigT:
    with open(path, "r") as f:
        config: ClusterConfigT = yaml.safe_load(f)
    
    ## Validate config...
    ver = config["VERSION"]
    assert isinstance(ver, str), "VERSION must be a string"
    if not isinstance(config, dict):
        raise ValueError("Config file must be a dict")
    if not isinstance(config["GLOBAL_ENV"], dict):
        raise ValueError("GLOBAL_ENVS must be a dict")
    if not isinstance(config["ENTRIES"], list):
        raise ValueError("ENTRIES must be a list")

    # for k in config["ENTRIES"]:
    #     assert k["name"] in allowed_entries, \
    #         f"Invalid entry name: {k['name']}"
    
    entries = config["ENTRIES"]
    for entry in entries:
        assert isinstance(entry, dict), "Entry must be a dict"
        assert "name" in entry, "Entry must have a name"
        assert entry['name'] in allowed_entries, f"Invalid entry name: {entry['name']}"
        if not 'env' in entry:
            entry['env'] = dict()
        if not 'args' in entry:
            entry['args'] = list()
        assert isinstance(entry["env"], dict), "env must be a dict"
        assert isinstance(entry["args"], list), "args must be a list"

    config["ENTRIES"] = entries

    return config


def cprint(*args):
    """ Custom print function """
    print(BCOLORS.LIGHTMAGENTA + "[cluster] " + " ".join(map(str, args)) + BCOLORS.ENDC)

## Multi-processes
def initProcesses(config: ClusterConfigT):
    """ Execute the config file """
    ps: list[subprocess.Popen] = []
    g_env = os.environ.copy()

    def __parseEnv(env:dict, dst: dict):
        for k, v in env.items():
            if v is None:
                if k in dst:
                    del dst[k]
            else:
                dst[k] = v

    def __execEntry(subcommand: str, entry: ConfigEntryT):
        this_env = g_env.copy()
        __parseEnv(entry.get("env", {}), dst = this_env)
        exec_args = ["lires", subcommand]
        args = entry.get("args", [])
        for arg in args:
            exec_args.append(str(arg))

        # print the command
        cprint(f"{' '.join(exec_args)}")

        ps.append(
            subprocess.Popen(
                exec_args,
                env = this_env,
                start_new_session=True,     # a new session makes the process independent from the parent, thus we can control it with SIGINT
            )
        )
    
    __parseEnv(config["GLOBAL_ENV"], dst = g_env)

    for entry in config["ENTRIES"]:
        __execEntry(entry["name"], entry)
    
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
