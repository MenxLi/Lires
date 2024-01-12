
import os


def unify_path(path):
    return os.path.abspath(os.path.expanduser(path))

class TestHomeStructure():

    def test_home_place(self):
        __this_dir = os.path.dirname(os.path.abspath(__file__))
        assert unify_path(os.environ["LRS_HOME"]) == unify_path(os.path.join(__this_dir, "..", "_test_home"))