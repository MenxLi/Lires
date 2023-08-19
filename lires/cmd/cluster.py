"""
Server clustering script.
It reads a yaml config file and starts the servers.

config file format:
----------------------------------------------------
ENVS:           <--- set global environment variables
    LRS_HOME: /path/to/lrs/home
    LRS_SSL_CERTFILE: /path/to/ssl/certfile | None
    LRS_SSL_KEYFILE: /path/to/ssl/keyfile | None
server:         <--- this is the name of the subcommand for lires
    -
        ENVS:     <--- set environment variables
            LRS_HOME: /path/to/lrs/home
        ARGS:      <--- command to run
            port : 8080
            iserver_host: localhost
            iserver_port: 8081
    -
        ENVS:
        ....
web:
    ...

iserver:
    ...
----------------------------------------------------
"""

from lires.confReader import LRS_HOME
from typing import TypedDict
import os, yaml, argparse, subprocess, signal, time, sys
import multiprocessing as mp

class ConfigEntryT(TypedDict):
    ENVS: dict
    ARGS: dict

class ClusterConfigT(TypedDict):
    ENVS: dict
    server: list[ConfigEntryT]
    web: list[ConfigEntryT]
    iserver: list[ConfigEntryT]

def __getDefaultConfig()->ClusterConfigT:
    ssl_certfile = os.environ.get("LRS_SSL_CERTFILE")
    ssl_keyfile = os.environ.get("LRS_SSL_KEYFILE")
    return {
        "ENVS": {
            "LRS_HOME": LRS_HOME,
            "LRS_SSL_CERTFILE": ssl_certfile,
            "LRS_SSL_KEYFILE": ssl_keyfile,
        },
        "server": [
            {
                "ENVS": {
                    "LRS_HOME": LRS_HOME,
                },
                "ARGS": {
                    "--port": 8080,
                    "--iserver_host": "localhost",
                    "--iserver_port": 8731,
                },
            }
        ],
        "web": [
            {
                "ENVS": {},
                "ARGS": {
                    "--port": 8081,
                },
            }
        ],
        "iserver": [
            {
                "ENVS": {
                    "OPENAI_API_KEY": "sk-xxxxx"
                },
                "ARGS": {
                    "--port": 8731,
                    "--host": "0.0.0.0",
                    "--openai-api-base": "https://api.openai.com/v1",
                    "--fastchat-api-base": "",
                },
            }
        ],
    }

def generateConfigFile(path:str):
    config = __getDefaultConfig()
    with open(path, "w") as f:
        yaml.safe_dump(config, f)
    
    comments = [
        "This is config file for lires cluster",
        "It serves as a script for starting multiple servers with different configurations",
        "The ENV variables are set globally, and can be overridden by the entries",
        "The entry name is the subcommand for `lires`",
        "Please refer to the `lires -h` for more information on the subcommands",
    ]
    # inject comments onto the top of the file
    with open(path, "r") as f:
        content = f.read()
    with open(path, "w") as f:
        f.write("# " + "\n# ".join(comments) + "\n\n")
        f.write(content)

def loadConfigFile(path:str)->ClusterConfigT:
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    
    ## Validate config...

    # check if config is valid
    if not isinstance(config, dict):
        raise ValueError("Config file must be a dict")

    for k in config.keys():
        assert k in ["ENVS", "server", "web", "iserver"], \
            "Config file keys must be in : ENVS, server, web, iserver"

    # check if ENVS is valid
    if not isinstance(config["ENVS"], dict):
        raise ValueError("ENVS must be a dict")

    # check if server, web, iserver are valid
    for k in ["server", "web", "iserver"]:
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


## Multi-processes
def initProcesses(config: ClusterConfigT):
    """
    Execute the config file
    """
    ps: list[mp.Process] = []
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
        __parseEnv(entry["ENVS"], this_environ)
        exec_args = ["lires", subcommand]
        for k, v in entry["ARGS"].items():
            exec_args.append(f"{k}")
            exec_args.append(str(v))
        
        # print(f"Environment: {this_environ}")
        # print(f"Executing: {' '.join(exec_args)}")
        # print("\n")

        ps.append(
            mp.Process(
                target=subprocess.run, 
                args = (exec_args,),
                kwargs = {"env": this_environ},
                daemon=True
            )
        )
    
    __parseEnv(config["ENVS"], g_environ)

    for key in ["server", "web", "iserver"]:
        for entry in config[key]:
            __execEntry(key, entry)
    
    return ps

def main():
    parser = argparse.ArgumentParser(description="Generate config file for lires cluster")
    parser.add_argument("path", type=str, help="path to the config file")
    parser.add_argument("--generate", action="store_true", help="generate config file")
    parser.add_argument("--yes", action="store_true", help="overwrite existing config file")
    args = parser.parse_args()

    if args.generate:
        if os.path.exists(args.path) and not args.yes:
            print("Config file already exists, use --yes to overwrite")
            exit(1)
        generateConfigFile(args.path)
        exit(0)
    
    if args.yes and not args.generate:
        print("--yes can only be used with --generate")
        exit(1)
    
    if not os.path.exists(args.path):
        print("Config file does not exist, use --generate to generate one")
        exit(1)
    
    config = loadConfigFile(args.path)
    procs =  initProcesses(config)
    print(f"Starting {len(procs)} processes...")

    for p in procs:
        p.start()

    # handle SIGINT
    def sigintHandler(sig, frame):
        print("SIGINT received, terminating...")
        for p in procs:
            p.terminate()
        # wait for all processes to terminate
        for p in procs:
            p.join()
        # somehow this is needed to make the terminal not messy...
        time.sleep(1)
        exit(0)

    signal.signal(signal.SIGINT, sigintHandler)
    
    for p in procs:
        p.join()

if __name__ == "__main__":
    main()