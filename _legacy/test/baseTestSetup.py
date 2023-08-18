import os, shutil, sys
from typing import List
import unittest
import subprocess


class TestBase(unittest.TestCase):
    FAIL_ALL: List[str] = []

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    def setUp(self) -> None:
        if self.FAIL_ALL:
            self.fail("Setup conditions not met: \n\t{}".format("\n\t".join(self.FAIL_ALL)))
        return super().setUp()

    @classmethod
    def setUpClass(cls) -> None:

        cls._setup_filePaths()
        cls._setup_test_filePaths()

        cls.setUpThisClass()
        return super().setUpClass()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.setUpThisClass()

        shutil.rmtree(os.environ["RBM_TEST_HOME"])
        return super().tearDownClass()

    @classmethod
    def setUpThisClass(cls) -> None:
        # Hook
        pass

    @classmethod
    def tearDownThisClass(cls) -> None:
        # Hook
        pass
    
    @classmethod
    def setFailFlag(cls, flag: str):
        cls.FAIL_ALL.append(flag)

    @classmethod
    def _setup_filePaths(cls):
        assert "RBM_TEMPLATE_HOME" in os.environ, "$RBM_TEMPLATE_HOME should be set before test"

        # set test data directory path
        if "RBM_TEST_HOME" in os.environ:
            os.environ["RBM_HOME"] = os.environ["RBM_TEST_HOME"]
        else:
            _DEFAULT_RBM_HOME = os.path.join(os.path.expanduser("~"), ".RBM")
            if not os.path.exists(_DEFAULT_RBM_HOME):
                os.mkdir(_DEFAULT_RBM_HOME)
            rbm_test_home = os.path.join(_DEFAULT_RBM_HOME, "test")
            os.environ["RBM_TEST_HOME"] = rbm_test_home
            os.environ["RBM_HOME"] = rbm_test_home

        # copy template home to test home
        shutil.copytree(os.environ["RBM_TEMPLATE_HOME"], os.environ["RBM_TEST_HOME"])

        # reset configuration file
        with open(os.devnull, "w") as fp:
            subprocess.check_call(["rbm-resetconf"], stdout=fp)

        # maybe generate database path
        from lires.confReader import getConf
        if not os.path.exists(getConf()["database"]):
            os.mkdir(getConf()["database"])

    @classmethod
    def _setup_test_filePaths(cls):
        from lires.confReader import RBM_HOME
        from lires.confReader import RBM_HOME
        from lires.confReader import TMP_DIR
        from lires.confReader import TMP_COVER, TMP_DB, TMP_WEB, TMP_WEB_NOTES
        from lires.confReader import CONF_FILE_PATH

        for cond in (
            RBM_HOME == os.environ["RBM_HOME"],
            RBM_HOME == os.environ["RBM_TEST_HOME"],
            RBM_HOME in TMP_DIR,
            TMP_DIR in TMP_COVER,
            TMP_DIR in TMP_WEB,
            TMP_DIR in TMP_DB,
            TMP_DIR in TMP_WEB_NOTES,
            os.path.exists(CONF_FILE_PATH),
        ):
            if not cond:
                cls.setFailFlag("File path test failed")
                return
    
    @property
    def rbm_config(self):
        from lires.confReader import getConf
        return getConf()

class MuteStdout:
    def __init__(self) -> None:
        self._default_sysout = sys.stdout
        self._dev_null = open(os.devnull, "w")

    @property
    def devnull(self):
        return self._dev_null

    def __enter__(self):
        sys.stdout = self._dev_null

    def __exit__(self, *args, **kwargs):
        sys.stdout = self._default_sysout
        self._dev_null.close()
