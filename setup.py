from setuptools import setup, find_packages
from resbibman.confReader import VERSION

setup(
    name="ResBibMan",
    version=VERSION,
    author="Mengxun Li",
    author_email="mengxunli@whu.edu.cn",
    description="A research paper manager",

    # 项目主页
    url="https://github.com/MenxLi/ResBibManager", 

    packages=find_packages(),

    classifiers = [
        #   Development Status
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.5",

    include_package_data = True,

    install_requires = ["PyQt5", "pybtex"],

    entry_points = {
        "console_scripts":[
            "resbibman=resbibman.exec:run",
            "rbm-resetConf=resbibman.cmdTools.generateDefaultConf:run"
        ]
    }
)