
from .base import *
import os, subprocess
import pytest

def unify_path(path):
    return os.path.abspath(os.path.expanduser(path))

class TestHomeStructure(BaseConfig):
    def test_homePlace(self):
        __this_dir = os.path.dirname(os.path.abspath(__file__))
        PASSED =  unify_path(os.environ["LRS_HOME"]) == unify_path(os.path.join(__this_dir, "..", "_sandbox"))
        assert PASSED, "LRS_HOME is not set correctly"
        if not PASSED:
            pytest.exit("LRS_HOME is not set correctly")

class TestInitUser(BaseConfig):
    def test_initUser(self):
        with utils.MuteEverything():
            os.system(
                "lrs-user add "
                f"{self.admin_user['username']} {self.admin_user['password']} "
                "--admin"
                )
            os.system(
                "lrs-user add "
                f"{self.normal_user['username']} {self.normal_user['password']} "
            )
        # check if user is added
        out = subprocess.check_output("lrs-user list", shell=True).decode("utf-8")
        assert len(out.strip().split("\n")) == 2
        assert self.admin_user["username"] in out
        assert self.normal_user["username"] in out