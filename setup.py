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

    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(),

    classifiers = [
        #   Development Status
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3"
    ],

    include_package_data = True,

    install_requires = ["PyQt5", "pybtex"],

    entry_points = {
        "console_scripts":[
            "resbibman=src.exec:main"
        ]
    }
)