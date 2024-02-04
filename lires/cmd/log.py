
import argparse, os, sys
import sqlite3
import glob
from typing import Optional, Generator
from lires.config import LOG_DIR
from lires.utils import BCOLORS

# f"""
# CREATE TABLE IF NOT EXISTS {name} (
#     time REAL, 
#     time_str TEXT,
#     level INTEGER,
#     level_name TEXT,
#     message TEXT
# )
# """
class LogDBReader:
    
    def __init__(self, db_file: str) -> None:

        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()
    
    def getTableNames(self) -> list[str]:
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [x[0] for x in self.cur.fetchall()]
    
    def hasTable(self, table_name: str) -> bool:
        self.cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        return len(self.cur.fetchall()) > 0
    
    def getMessagesFromTable(
        self, 
        table_name: str, 
        level_name: Optional[str] = None,
        limit: int = 9999999) -> list[tuple]:
        if level_name is None:
            self.cur.execute(f"SELECT * FROM {table_name} ORDER BY time DESC LIMIT {limit}")
        else:
            self.cur.execute(f"SELECT * FROM {table_name} WHERE level_name='{level_name}' ORDER BY time DESC LIMIT {limit}")
        return self.cur.fetchall()
    
    def getCountFromTable(
        self, 
        table_name: str, 
        level_name: Optional[str] = None) -> int:
        if level_name is None:
            self.cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        else:
            self.cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE level_name='{level_name}'")
        return self.cur.fetchone()[0]

__color_level = {
    "DEBUG": BCOLORS.OKBLUE,
    "INFO": BCOLORS.OKGREEN,
    "WARNING": BCOLORS.WARNING,
    "ERROR": BCOLORS.FAIL,
    "CRITICAL": BCOLORS.FAIL,
}
def formatLine(line: tuple) -> str:
    time = line[1]
    level_name = line[3]
    message = line[4]
    return f"{BCOLORS.OKCYAN}{time}{BCOLORS.ENDC} {__color_level[level_name]}{level_name}{BCOLORS.ENDC}: {message}"
def formatLines(lines: list[tuple]) -> Generator[str, None, None]:
    for i in range(0, len(lines)):
        yield formatLine(lines[i])

def sortLines(lines: list[tuple]) -> list[tuple]:
    # in the order of time
    return sorted(lines, key=lambda x: x[0], reverse=False)

def main():
    parser = argparse.ArgumentParser(description='Log tools')
    sp = parser.add_subparsers(dest='subparser_name', help='sub-command help')
    sp_view = sp.add_parser('view', help='View log, output to stdout')
    sp_view.add_argument('-i', '--inputs', type=str, dest='files',
                        nargs='+', default=glob.glob(f"{LOG_DIR}/*.sqlite*"), 
                        help='Log database files')
    sp_view.add_argument('-l', '--level', type=str, help='Log level', default=None)
    sp_view.add_argument('-t', '--table', type=str, help='Table name', default=None)
    sp_view.add_argument('--limit', type=int, help='Limit number of lines', default=9999)

    sp_check = sp.add_parser('check', help='Check log table, output to stdout')
    sp_check.add_argument('-i', "--inputs", dest = "files",
                        type=str, nargs='+', default=glob.glob(f"{LOG_DIR}/*.sqlite"), 
                        help='Log database files')
    sp_check.add_argument('-l', '--level', type=str, help='Log level', default=None)

    
    args = parser.parse_args()

    if not args.subparser_name:
        parser.print_help()
        return
    
    def getAllTableNames(files) -> list[str]:
        __all_table_names = []
        for file in files:
            reader = LogDBReader(file)
            __all_table_names.extend(reader.getTableNames())
        return sorted(list(set(__all_table_names)))
    
    if args.subparser_name == 'view':
        __all_lines = []
        table_name = args.table
        __all_table_names = getAllTableNames(args.files)
        if table_name is None or table_name == "":
            for idx, table_name in enumerate(__all_table_names):
                print(f"[{idx}] {table_name}")
            print(
                "The table name is not specified, please choose one from above, "
                "or start the command with '-t' option"
                )
            inp = input("Choose a table: ")
            if inp.isdigit():
                table_name = __all_table_names[int(inp)]
            else:
                exit(1)
        
        if table_name not in __all_table_names:
            # try to find a potential table name
            pot_names = []
            for name in __all_table_names:
                if name.startswith(table_name):
                    pot_names.append(name)
            if len(pot_names) == 0:
                print(f"Cannot find table name {table_name}")
                exit(1)
            elif len(pot_names) > 1:
                print(f"Multiple table names found: {pot_names}")
                exit(1)
            else:
                table_name = pot_names[0]

        for file in args.files:
            reader = LogDBReader(file)
            if not reader.hasTable(table_name):
                continue
            lines = reader.getMessagesFromTable(table_name, args.level, limit=args.limit)
            __all_lines.extend(lines)
        __all_lines = sortLines(__all_lines)
        try:
            for line in formatLines(__all_lines):
                print(line)
            print('\n'+'-' * 80)
            print(f"Total {len(__all_lines)} lines, from table {table_name}")
        except BrokenPipeError:
            # https://stackoverflow.com/a/58517082
            # Python flushes standard streams on exit; redirect remaining output
            # to devnull to avoid another BrokenPipeError at shutdown
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)  # Python exits with error code 1 on EPIPE


    elif args.subparser_name == 'check':
        # get size of each table
        all_tables = getAllTableNames(args.files)
        count = {}
        for file in args.files:
            reader = LogDBReader(file)
            for table_name in all_tables:
                if not reader.hasTable(table_name):
                    continue
                lines = reader.getCountFromTable(table_name, level_name=args.level)
                count[table_name] = count.setdefault(table_name, 0) + lines
        # print
        max_len = max([len(x) for x in all_tables])
        digit_len = max(len(str(max(count.values()))), 5)
        line_len = max_len + digit_len + 3
        print("+" + "-" * (line_len-2) + "+")
        print( "|TABLE_NAME".ljust(max_len + 1, ' ') + f"|{'COUNT'.ljust(digit_len)}|")
        print( "|"+"-"*max_len + f"|{'-'*digit_len}|")
        for table_name in all_tables:
            print(f"|{table_name:<{max_len}}|{count[table_name].__str__().ljust(digit_len, ' ')}|")
        print("+" + "-" * (line_len-2) + "+")
        
    else:
        raise ValueError(f"Unknown subparser name: {args.subparser_name}")

if __name__ == "__main__":
    main()