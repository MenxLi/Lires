import argparse, asyncio, json

def main():
    parser = argparse.ArgumentParser(description="Query status of lires")
    parser.add_argument("--registry", action="store_true", help="show registry status")
    parser.add_argument("--process", action="store_true", help="show running processes")
    args = parser.parse_args()

    if args.process:
        # try to find all process that contains "lires"
        import subprocess
        import psutil

        # get all process
        proc = subprocess.Popen(["ps", "-A"], stdout=subprocess.PIPE)
        out, err = proc.communicate()
        out = out.decode("utf-8")

        # find all process that contains "lires"
        __to_kill = []
        for line in out.splitlines():
            if "lires" in line:
                pid = int(line.split(None, 1)[0])
                __to_kill.append(pid)

        # print all process to kill
        for idx, pid in enumerate(__to_kill):
            p = psutil.Process(pid)
            print(f"{idx}. {pid}: {p.name()}\n{' '.join(p.cmdline())}\n")
    
    elif args.registry:
        from lires.api import RegistryConn
        rconn = RegistryConn()
        res = asyncio.run(rconn.view())
        print(json.dumps(res, indent=4))
        
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()