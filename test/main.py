
import subprocess, os, time, shutil, threading

def startSubprocess(cmd):
    # import sys
    # process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def watchProcess():
        while True:
            time.sleep(0.1)
            if process.poll() is not None:
                print("ERROR: subprocess exited unexpectedly ({})".format(cmd))
                return

    threading.Thread(target=watchProcess, daemon=True).start()
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

    # it's important to set LRS_HOME!
    __this_dir = os.path.dirname(os.path.abspath(__file__))
    LRS_HOME = os.path.join(__this_dir, "_test_home")
    os.environ["LRS_HOME"] = LRS_HOME
    # to disable log output
    os.environ["LRS_LOG_LEVEL"] = "CRITICAL"

    # prepare for test
    subprocess.check_call("lrs-resetconf", shell=True)
    startSubprocess("lires server")
    # to avoid resource conflict!
    # during initialization, the server will try to create some files
    # and if the file simultaneously being used by other process, it will fail
    time.sleep(0.1)
    startSubprocess("lires iserver")
    print("Waiting for server to start...")
    watchForStartSign()
    
    _test_cmd = "python3 -m unittest discover -s test/cases -p 'test_*.py'"
    subprocess.check_call(_test_cmd, shell=True)

    # clean up
    print("Test done, cleaning up.")
    input("Press enter to continue...")
    shutil.rmtree(LRS_HOME)