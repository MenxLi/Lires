import os, platform, subprocess, time, random, shutil
import tempfile

__this_dir = os.path.dirname(os.path.abspath(__file__))
eigen_src_path = os.path.join(__this_dir, 'external', "eigen_src")

def checkCommandExists(cmd: str) -> bool:
    if platform.system() == "Windows":
        return subprocess.call(["where", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    return subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def initEigenSrc(eigen_version: str = "3.4.0"):
    global eigen_src_path
    if os.path.exists(eigen_src_path):
        if input(f"Eigen source code already exists in [{eigen_src_path}], do you want to remove it? [y/N]: ").strip().lower() == "y":
            shutil.rmtree(eigen_src_path)
        else:
            return
    os.makedirs(eigen_src_path)

    __downloading_lock_file = os.path.join(tempfile.gettempdir(), "lires_eigen_downloading.lock")
    while os.path.exists(__downloading_lock_file):
        print(f"Find lock file [{__downloading_lock_file}], waiting...")
        time.sleep(random.random() * 1 + 1)     # wait for 1~2 seconds, avoid resource competition

    if os.listdir(eigen_src_path) == [] or \
        not os.path.exists(os.path.join(eigen_src_path, "Eigen", "src", "Core")):

        print("Downloading Eigen...")
        if not checkCommandExists("git"):
            raise RuntimeError("git not found.")
        
        open(__downloading_lock_file, "w").close()
        try:
            subprocess.check_call([
                "git", "clone", "--depth=1", f"--branch={eigen_version}",
                "https://gitlab.com/libeigen/eigen.git", eigen_src_path]
                )
        except: pass
        finally:
            os.remove(__downloading_lock_file)