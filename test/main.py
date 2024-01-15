
import subprocess, os, time, shutil, threading, argparse

EXITING = False
def startSubprocess(cmd):
    global EXITING
    # import sys
    # process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def watchProcess():
        while True:
            time.sleep(0.1)
            if process.poll() is None:
                continue
            if EXITING: 
                return
            print("ERROR: subprocess exited unexpectedly ({})".format(cmd))
            return
    threading.Thread(target=watchProcess, daemon=True).start()

    return process

def watchForStartSign():
    time.sleep(5)
    return 

    # TODO: implement this...
    from lires.config import LOG_DIR

    def isIserverReady():
        _log_f = os.path.join(LOG_DIR, "iserver.log")
        if not os.path.exists(_log_f):
            return False

        with open(_log_f, "r") as f:
            if "Warmup done!" in f.read():
                return True
        return False

    while True:
        time.sleep(0.1)
        if isIserverReady():
            return


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', "--verbose", action="store_true")
    parser.add_argument("--no-server", action="store_true")
    args = parser.parse_args()

    __this_dir = os.path.dirname(os.path.abspath(__file__))
    __project_dir = os.path.dirname(__this_dir)
    assert os.getcwd() == __project_dir, "Please run this script from project root directory"

    # it's important to set LRS_HOME!
    LRS_HOME = os.path.join(__this_dir, "_test_home")
    os.environ["LRS_HOME"] = LRS_HOME
    # to disable log output
    os.environ["LRS_LOG_LEVEL"] = "CRITICAL" if not args.verbose else "DEBUG"

    # prepare for test
    procs = []
    if not args.no_server:
        subprocess.check_call("lrs-resetconf", shell=True)
        procs.append(startSubprocess("lires server"))
        # to avoid resource conflict!
        # during initialization, the server will try to create some files
        # and if the file simultaneously being used by other process, it will fail
        time.sleep(0.1)
        procs.append(startSubprocess("lires iserver"))
        print("Waiting for server to start...")
        watchForStartSign()
    
    _report_file = os.path.join(__this_dir, "_cache", "output", "report.html")
    _test_case_dir = os.path.join(__this_dir, "cases")
    _test_cmd = f"pytest {'-s' if args.verbose else ''} --html={_report_file} {_test_case_dir}"
    try:
        subprocess.check_call(_test_cmd, shell=True)
    except Exception as e:
        print("Error while running the tests: ", e)

    # clean up
    print("Test done, cleaning up.")
    input("Press enter to continue...")
    # kill all subprocesses
    EXITING = True
    for proc in procs:
        proc.kill()
    for proc in procs:
        proc.wait()
    # remove test home
    shutil.rmtree(LRS_HOME)

    formatFilePath = lambda x: f"{os.path.relpath(x, start=__project_dir)}"
    print(f"Done. check report at: {formatFilePath(_report_file)}")