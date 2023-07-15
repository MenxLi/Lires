
"""
Compile binary with pyinstaller
"""
import argparse
import subprocess
import platform

PROG_NAME = "rbm"

def compileMain(addtional_flags: list):

    hidden_imports = ["PyQt6.QtWebChannel", "PyQt6.QtNetwork", "PyQt6.QtWebEngineCore", "PyQt6.QtPrintSupport"]

    data_path = [
    ( "resbibman/version.yaml", "./resbibman" ),

    ( "resbibman/icons/*", "./resbibman/icons" ),
    ( "resbibman/assets/*", "./resbibman/assets" ),

    ( "resbibman/docs/*.md", "./resbibman/docs" ),
    ( "resbibman/docs/imgs/*", "./resbibman/docs/imgs" ),

    ( "resbibman/stylesheets/*.qss", "./resbibman/stylesheets" ),
    ( "resbibman/stylesheets/Breeze", "./resbibman/stylesheets/Breeze" ),

    ( "packages/QCollapsibleCheckList/QCollapsibleCheckList/icons/*", \
        "./QCollapsibleCheckList/icons" ),
    ]

    cmd = ["pyinstaller", "--noconfirm", "-w", "-n", PROG_NAME, "-i", "./resbibman/icons/resbibmanicon/favicon.ico", "./__main__.py", "--additional-hooks-dir=pyinstallerHooks"]
    cmd += addtional_flags

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

def compileRunScript(additional_flags: list):
    import tempfile, os
    tf = tempfile.NamedTemporaryFile(mode = "w", suffix=".py", delete=False)
    tf.write("import subprocess, sys;args = sys.argv[1:];cmd = ['resbibman'] + args;subprocess.check_call(cmd)")
    tf.close()
    tmp_script = tf.name
    cmd = ["pyinstaller", "--noconfirm", "-w", "-n", PROG_NAME, "-i", "./resbibman/icons/resbibmanicon/favicon.ico", tmp_script]
    cmd += additional_flags
    subprocess.check_call(cmd)

    if os.path.exists(tmp_script):
        os.remove(tmp_script)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--script", action="store_true", help="\
        Soft/Script flag, \
        Compile as an executable calling subprocess 'resbibman ...'\n\
        Should install the app by pip in prior to using the executable\
    ")
    parser.add_argument("--onefile", action="store_true", help="bulid single file application")
    args = parser.parse_args()

    additional_flags = []
    if args.onefile:
        additional_flags.append("--onefile")

    if args.script:
        print("Compiling run script command")
        compileRunScript(additional_flags)
    else:
        compileMain(additional_flags)
