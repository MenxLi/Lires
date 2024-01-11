
import subprocess, os, time

def startSubprocess(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return process

def watchForStartSign():
    from lires.config import LOG_DIR
    _log_f = os.path.join(LOG_DIR, "iserver.log")
    while True:
        time.sleep(0.1)

        if not os.path.exists(_log_f):
            print("Error: log file not found")
            exit(1)

        with open(_log_f, "r") as f:
            if "Warmup done!" in f.read():
                return

if __name__ == "__main__":

    # to disable log output
    os.environ["LRS_LOG_LEVEL"] = "CRITICAL"

    subprocess.check_call("lrs-resetconf", shell=True)
    startSubprocess("lires server")
    startSubprocess("lires iserver")
    
    print("Waiting for server to start...")
    watchForStartSign()
    
    _test_cmd = "python3 -m unittest discover -s test/cases -p 'test_*.py'"
    subprocess.check_call(_test_cmd, shell=True)