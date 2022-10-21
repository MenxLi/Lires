
"""
Compile binary with pyinstaller
"""

import subprocess, platform

hidden_imports = ["PyQt6.QtWebChannel", "PyQt6.QtNetwork", "PyQt6.QtWebEngineCore", "PyQt6.QtPrintSupport"]

data_path = [
( "resbibman/icons/*", "./resbibman/icons" ),
( "resbibman/assets/*", "./resbibman/assets" ),

( "resbibman/docs/*.md", "./resbibman/docs" ),
( "resbibman/docs/bibtexTemplates/*", "./resbibman/docs/bibtexTemplates" ),
( "resbibman/docs/imgs/*", "./resbibman/docs/imgs" ),

( "resbibman/stylesheets/*.qss", "./resbibman/stylesheets" ),
( "resbibman/stylesheets/Breeze", "./resbibman/stylesheets/Breeze" ),

( "RBMWeb/frontend/*", "./RBMWeb/frontend" ),
]

cmd = ["pyinstaller", "--noconfirm", "-w", "-i", "./resbibman/icons/resbibmanicon/favicon.ico", "./__main__.py", "--additional-hooks-dir=pyinstallerHooks"]

for himp in hidden_imports:
    cmd += ["--hidden-import", himp]

if platform.system() == "Windows":
    sep = ";"
else: 
    sep = ":"
for data in data_path:
    cmd += ["--add-data", '{src}{sep}{dst}'\
            .format(src = data[0], sep=sep, dst = data[1])]

print(" ".join(cmd))
subprocess.check_call(cmd)
