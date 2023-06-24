import os, platform
from setuptools import setup, find_packages
from resbibman.version import VERSION

with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as fp:
    install_requires = [pkg for pkg in fp.read().split("\n") if pkg]

with open(os.path.join(os.path.dirname(__file__), "iRBM", "requirements.txt")) as fp:
    ai_requires = [pkg for pkg in fp.read().split("\n") if pkg]

with open(os.path.join(os.path.dirname(__file__), "requirements-dev.txt")) as fp:
    dev_requires = [pkg for pkg in fp.read().split("\n") if pkg]

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

    install_requires = install_requires,
    extras_require= {
        "ai": ai_requires,
        "full": ai_requires + dev_requires
    },

    entry_points = {
        "console_scripts":[
            "resbibman=resbibman.exec:run",
            "rbm-resetconf=resbibman.cmd.generateDefaultConf:run",
            "rbm-collect=resbibman.cmd.rbmCollect:main",
            "rbm-utils=resbibman.cmd.miscUtils:main",
            "rbm-share=resbibman.cmd.rbmShare:main",
            "rbm-keyman=resbibman.cmd.manageKey:run",
            "rbm-discuss=resbibman.cmd.rbmDiscuss:main",
            "rbm-index=resbibman.cmd.index:main",
        ]
    }
)
