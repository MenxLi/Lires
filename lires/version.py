from typing import Dict
import yaml, os

__this_dir = os.path.dirname(__file__)
_yaml_version_file = os.path.join(__this_dir, "version.yaml")

with open(_yaml_version_file, "r", encoding='utf-8') as fp:
    version_histories: Dict[str, list[dict[str, list[str]] | str]] = yaml.safe_load(fp)["version_history"]

VERSION_HISTORIES: list[tuple[str, list[dict[str, list[str]] | str]]] = []
for v, h in version_histories.items():
    # validity check, 
    # v should be string, h should be list
    # the value in h should be string or dict of one key and one value
    # the value in the dict should be list of strings
    assert isinstance(v, str)
    assert isinstance(h, list)
    for i in h:
        if isinstance(i, str):
            continue
        assert isinstance(i, dict)
        assert len(i) == 1
        val = list(i.values())[0]
        assert isinstance(val, list)
        for j in val[0]:
            assert isinstance(j, str)
    VERSION_HISTORIES.append((v, h))
VERSION, DESCRIPEITON = VERSION_HISTORIES[-1]
VERSION = VERSION.split("-")[0].strip()

__all__ = ["VERSION", "DESCRIPEITON", "VERSION_HISTORIES"]