# Data/Library Files necessary for pyinstaller to build excutable

[Pyinstaller-Spec](http://pyinstaller.readthedocs.io/en/stable/spec-files.html#adding-data-files)

`pyi-makespec -i ./resbibman/icons/resbibmanicon/favicon.ico ./__main__.py --additional-hooks-dir=pyinstallerHooks --hidden-import PyQt6.QtWebChannel --hidden-import PyQt6.QtNetwork --hidden-import PyQt6.QtWebEngineCore --hidden-import PyQt6.QtPrintSupport`

```Python

data_path = [
( "resbibman/conf.json", "./resbibman" ),
( "resbibman/docs/*", "./resbibman/docs" ),
( "resbibman/icons/*", "./resbibman/icons" ),
( "resbibman/assets/*", "./resbibman/assets" ),
( "resbibman/stylesheets/*", "./resbibman/stylesheets" ),

( "RBMWeb/backend/config.json", "./RBMWeb/backend" ),
( "RBMWeb/frontend/*", "./RBMWeb/frontend" ),
]

hiddenimports=["PyQt6.QtWebChannel", "PyQt6.QtNetwork", "PyQt6.QtWebEngineCore", "PyQt6.QtPrintSupport"]

```
