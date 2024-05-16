"""
Generate requeriments from pyproject.toml and print to stdout, 
for use with docker build

NOTE: tomllib is added in 3.11
"""

import os, sys, itertools

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

def getPyProject():
    # check python version
    if sys.version_info < (3, 11):
        # check if tomlkit is installed
        try:
            import tomlkit
        except ImportError:
            os.system("pip install tomlkit")
            import tomlkit
        with open(os.path.join(THIS_DIR, "pyproject.toml")) as f:
            return tomlkit.parse(f.read())
    
    else:
        import tomllib
        with open(os.path.join(THIS_DIR, "pyproject.toml")) as f:
            return tomllib.loads(f.read())

def getDeps(pyproj: dict):

    init_deps = pyproj.get('build-system', {}).get('requires', [])
    assert pyproj.get('build-system', {}).get('build-backend') == 'setuptools.build_meta'

    base_deps = pyproj.get('project', {}).get('dependencies', {})

    extra_dep_keys = [
        'core', 'ai'
    ]
    extra_deps = itertools.chain.from_iterable([
        pyproj.get('project', {}).get('optional-dependencies', {}).get(key, [])
        for key in extra_dep_keys
        ])
    
    return itertools.chain(init_deps, base_deps, extra_deps)

if __name__ == "__main__":
    pyproj = getPyProject()
    deps = getDeps(pyproj)
    print("\n".join(deps))