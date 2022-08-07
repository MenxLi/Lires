import os, platform
from setuptools import setup, find_packages
from resbibman.confReader import VERSION

with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as fp:
    install_requires = [pkg for pkg in fp.read().split("\n") if pkg]

    if platform.system() == "Darwin" and platform.processor() == "arm":
        # Apple silicon
        for i in range(0, len(install_requires))[::-1]:
            if install_requires[i] == "PyMuPDF":
                # Not install PyMuPDF in MacOS, can't compile for now
                install_requires.pop(i)

setup(
    name="ResBibMan",
    version=VERSION,
    author="Mengxun Li",
    author_email="mengxunli@whu.edu.cn",
    description="A research paper manager.",

    # 项目主页
    url="https://github.com/MenxLi/ResBibManager", 

    packages=find_packages(),

    classifiers = [
        #   Development Status
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.8.0",      # TypedDict was introduced after 3.8

    include_package_data = True,

    #  install_requires = \
    #  ["PyQt5", "pybtex", "pyperclip", "PyMuPDF>=1.19.3", "PyQtWebEngine", "markdown", "tornado", "requests", "watchdog", "nest_asyncio", "arxiv"],
    install_requires = install_requires,

    entry_points = {
        "console_scripts":[
            "resbibman=resbibman.exec:run",
            "rbm-resetconf=resbibman.cmdTools.generateDefaultConf:run",
            "rbm-collect=resbibman.cmdTools.rbmCollect:main",
            "rbm-keyman=RBMWeb.cmd.manageKey:run",
            "rbm-discuss=RBMWeb.cmd.rbmDiscuss:main",
        ]
    }
)
