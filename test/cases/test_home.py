
import os
import unittest


def unify_path(path):
    return os.path.abspath(os.path.expanduser(path))

class TestHomeStructure(unittest.TestCase):

    def test_home_place(self):
        __this_dir = os.path.dirname(os.path.abspath(__file__))
        self.assertTrue(
            unify_path(os.environ["LRS_HOME"]) == unify_path(os.path.join(__this_dir, "..", "_test_home"))
            )