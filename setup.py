from __future__ import annotations
from setuptools import setup, find_packages
import yaml, os
import glob

__this_dir = os.path.dirname(__file__)

_yaml_version_file = os.path.join(__this_dir, "lires", "version.yaml")
with open(_yaml_version_file, "r", encoding='utf-8') as fp:
    version_histories: dict[str, list[str]] = yaml.safe_load(fp)["version_history"]
_VERSION_HISTORIES = []
for v, h in version_histories.items():
    v = v.split("-")[0].strip()
    _VERSION_HISTORIES.append((v, h))
VERSION, _ = _VERSION_HISTORIES[-1]

def vectorLibExt():
    from pybind11.setup_helpers import Pybind11Extension, ParallelCompile, naive_recompile
    ParallelCompile("NPY_NUM_BUILD_JOBS", needs_recompile=naive_recompile, default=4).install()
    source_dir = './lires/vector/c'
    eigen_dir = './external/eigen'
    compile_files = [ os.path.relpath(f, __this_dir) for f in glob.glob(os.path.join(source_dir, "*.cpp"), recursive=True)]
    include_dirs = [source_dir, eigen_dir]
    return [
        Pybind11Extension(
            "lires.vector.lib.impl{}".format(vector_dim),
            compile_files,
            define_macros=[
                ("FEAT_DIM", vector_dim), 
                ("MODULE_NAME", "impl{}".format(vector_dim)),
                ("NDEBUG", None),
                ],
            include_dirs=include_dirs,
            cxx_std=17,
            language="c++",
            # add some optimization flags
            extra_compile_args=["-O2", '-funroll-loops'] # '-march=native', '-mtune=native', '-fopenmp'],
        )
        for vector_dim in [768]
    ]

setup(
    name="Lires",
    version=VERSION,
    packages=find_packages(),
    include_package_data = True,
    ext_modules=vectorLibExt(),
)
