import os
import curses
from lires.config import LOG_DIR

__all_log_files = os.listdir(LOG_DIR)
__all_log_files.sort()
__g_files = {}
def show(stdscr: curses.window):

    # Turn off cursor blinking
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.curs_set(0)
    current_row = 0
    for _, row in enumerate(__all_log_files):
        if not row in __g_files:
            with open(os.path.join(LOG_DIR, row), "r", encoding="utf-8") as fp:
                n_lines = len(fp.readlines())
            # if n_lines > 0:
            __g_files[row] = n_lines
    # Print the menu
    print_menu(stdscr, current_row, __g_files)
    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP or key == ord('k') and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN or key == ord('j') and current_row < len(__g_files)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            openWithTerm(__all_log_files[current_row])
            exit(0)
        elif key == curses.KEY_BACKSPACE or key == curses.KEY_LEFT or key == ord('q') or key == 27:
            exit(0)
        elif key == ord('G'):
            current_row = len(__all_log_files)-1
        elif key == ord('g'):
            # TODO: support gg
            current_row = 0
        else:
            pass
        print_menu(stdscr, current_row, __g_files)


def print_menu(stdscr: curses.window, row, n_lines_dict: dict[str, int]):
    stdscr.clear()
    LEN = 48
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, w//2 - LEN//2 - 1, "Press 'q' to exit")
    for idx, v in enumerate(n_lines_dict.items()):
        key, n_lines = v
        to_show = f"{key}"
        __n_count = len(str(n_lines))
        # format to same length
        if len(to_show) + __n_count < LEN:
            to_show = to_show + " " * (LEN - len(to_show) - __n_count)
        else:
            to_show = to_show[:LEN-__n_count-3] + "..."
        to_show = f"{'' if idx != row else '>'} {to_show} ({n_lines})"
        
        x = w//2 - LEN//2 - 1
        y = h//2 - len(n_lines_dict)//2 + idx - 1

        if idx == row:
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(y, x, to_show)
            stdscr.attroff(curses.color_pair(3))
        elif n_lines == 0:
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(y, x, to_show)
            stdscr.attroff(curses.color_pair(2))
        else:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, to_show)
            stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()


def openWithTerm(log_file: str):
    import platform, subprocess
    if platform.system() == "Windows":
        subprocess.call(["more", os.path.join(LOG_DIR, log_file)])
    else:
        subprocess.call(["less", os.path.join(LOG_DIR, log_file)])

def main():
    curses.wrapper(show)

if __name__ == '__main__':
    main()