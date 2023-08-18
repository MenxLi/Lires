from __future__ import annotations
from setuptools import setup, find_packages
import yaml, os

__this_dir = os.path.dirname(__file__)

_yaml_version_file = os.path.join(__this_dir, "lires", "version.yaml")
with open(_yaml_version_file, "r", encoding='utf-8') as fp:
    version_histories: dict[str, list[str]] = yaml.safe_load(fp)["version_history"]
_VERSION_HISTORIES = []
for v, h in version_histories.items():
    _VERSION_HISTORIES.append((v, "; ".join(h)))
VERSION, DESCRIPEITON = _VERSION_HISTORIES[-1]

_license_file = os.path.join(__this_dir, "LICENSE")
with open(_license_file, "r", encoding='utf-8') as fp:
    LICENSE = fp.read()

setup(
    version=VERSION,
    packages=find_packages(),
    include_package_data = True,
    license=LICENSE,
)
