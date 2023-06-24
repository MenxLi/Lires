from typing import Dict, List
import yaml, os

__this_dir = os.path.dirname(__file__)
_yaml_version_file = os.path.join(__this_dir, "version.yaml")

with open(_yaml_version_file, "r", encoding='utf-8') as fp:
    version_histories: Dict[str, List[str]] = yaml.safe_load(fp)["version_history"]

_VERSION_HISTORIES = []
for v, h in version_histories.items():
    _VERSION_HISTORIES.append((v, "; ".join(h)))
VERSION, DESCRIPEITON = _VERSION_HISTORIES[-1]

#===========================================#
## DEPRECATED ##
__VERSION_HISTORIES__ = [
    ("0.0.1 - Alpha", "Under development"),
    ("0.0.2 - Alpha", "Under development: Added tag related functions"),
    ("0.0.3 - Alpha", "Under development: Internal code structure change"),
    ("0.0.4", "Added search tools, toolbar, and application style"),
    ("0.1.0", "Finished toolbar, bug fix, use setup.py for distribution"),
    ("0.1.1", "Add bibtex template, Bug fix"),
    ("0.1.2", "Using argparse when starting, add window icon"),
    ("0.1.3", "Added log file"),
    ("0.2.0", "Use table view"),
    ("0.2.1", "Add context menu"),
    ("0.2.2", "Add pending window, support entry without file"),
    ("0.2.3", "Better support for entry without file"),
    ("0.2.4", "Better support for pending window, add pdf preview to pending window"),
    ("0.2.5", "Enable drag-drop in info panel to add file"),
    ("0.2.6", "Context menu, better documentation"),
    ("0.2.7", "Add markdown render window"),
    ("0.2.8", "Add markdown editor syntax highlight (basic)"),
    ("0.2.9", "UI update"),
    ("0.2.10", "Better support for proceedings and better copy citation"),
    ("0.2.11", "Bug fix: not updating file tag; implement open file location in context menu"),
    ("0.2.12", "Add Cover to info panel"),
    ("0.2.13", "Bug fix: update fitz method naming, use integer value resize"),
    ("0.2.14", "Better image insertion, allow copy paste and drag"),
    ("0.2.15", "Add free document option into file selector"),
    ("0.2.16", "Add url/doi into file info panel"),
    ("0.3.0", "Web viewer!"),
    ("0.3.1", "Icon change & update setup.py distribution & argparse update."),
    ("0.3.2", "Frontend add server query."),
    ("0.3.3", "Frontend add banner (reload database, search), UI update, change frontend server to tornado server, "\
     "start front end and backend with single python cmd argument."),
    ("0.3.4", "Frontend small update. change backend port to 8079"),
    ("0.3.5", "Now can insert no-file entry by cancel in file selection prompt; Add file size to file info"),
    ("0.3.6", "API update: Change resbibman.backend to resbibman.core"),
    ("0.3.7", "Bug fix: edit weburl or switch mdTab would lead to crash when no file is selected"),
    ("0.3.8", "Use one server to start front and backend"),
    ("0.3.9", "Check if file exists, while adding; change cloud icon"),
    ("0.3.10", "Asynchronous comment saving; use logger instead of print"),
    ("0.3.11", "Allow bibtex editing"),
    ("0.3.12", "More bibtex template"),
    ("0.3.13", "Not automatically save comment, show comment save indicator on info panel; reset_conf option in CLI"),
    ("0.4.0", "Offline html support"),
    ("0.4.1", "Panel collapse buttons; Markdown highlight improvements; UI changes; Minor bug fixes"),
    ("0.5.0", "Online mode!!"),
    ("0.5.1", "Synchronize strategy update; GUI host settings; PDF cover cache; Move some window to dialog class; Clear cache CLI"),
    ("0.5.2", "Asynchronous UI update when connection; Improved watch file changes; Bug fix: basename now not allowed to have question mark"),
    ("0.5.3", "Better file modification monitering; Bug fix: rename/delete tag now will affact unasynchronized data; CLI change"),
    ("0.5.4", "Document update; Use asyncio to accelerate dataloading; Add delete to context menu of file selector; "\
     "CLI update; Bug fixs: rbmweb can serve packed webpages with style, server can serve empty database"),
    ("0.6.0", "Online discussion avaliable; Info file record time as floating time stamp; Key login required for accessing webpage; "\
     "rbm-collect/rbm-discuss; Server can serve notes in html format"),
    ("0.6.0a", "Using PyQt6! View comment preview in online mode"),
    ("0.6.1", "Comment CSS update; Full screen; Bug fixes"),
    ("0.6.2", "Propmt conflict resolving when synchroning; Bug fixes: Now, delete old temp_db when server change, invalid bibtex input won't crash the program, etc."),
    ("0.6.3", "Better logging in log file; Stricter frontend access key requirements; Added update script"),
    ("0.6.4", "Preset server configuration; Scroll online markdown in GUI; Server-side docker deployment; "\
     "Delete cache and prompt user of unsynced data when quitting; Bug fixes: Not freeze GUI if server is down"),
    ("0.6.5", "Latex equation support; Toggle panel button only show one panel; Being able to export data; Log exceptions"),
    ("0.6.6", "Better log; Discussion tab; markdown color font style; More help options; Binary distribution"),
    ("0.6.7", "UI update: more help options; Font size in configuration file; Dark theme icon color; Context menu separator; "\
     "Better macos and windows file watcher; Kill statusbar updating thread after quitting"),
    ("0.6.8", "Convert bibtex from nbib; Argparser update; Global configuration buffer; Switch server without restarting"),
    ("0.6.9", "Being able to add bib&nbib file; Not deleting original document when adding to database; Bug fixes: mayn not delete remote file"),
    ("0.6.10", "New RBMWeb sharing page; Hover highlight entire line; Add menubar, toolbar can be hidden; Font settings; "\
     "Move cache dir out of system tempdir; Sync bug fixes on Macos;"),
    ("0.7.0", "Use RBM_HOME directory for application data storage; Load font settings without restart; Bug fixes"),
]
## DEPRECATED ##
#===========================================#
