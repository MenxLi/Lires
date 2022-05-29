from setuptools import setup, find_packages
from resbibman.confReader import VERSION

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

    install_requires = ["PyQt5", "pybtex", "pyperclip", "PyMuPDF>=1.19.3", "PyQtWebEngine", "markdown", "tornado", "requests", "watchdog", "nest_asyncio"],

    entry_points = {
        "console_scripts":[
            "resbibman=resbibman.exec:run",
            "rbm-resetConf=resbibman.cmdTools.generateDefaultConf:run",
            "rbm-keyman=RBMWeb.cmd.manageKey:run"
        ]
    }
)
