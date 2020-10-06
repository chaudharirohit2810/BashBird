import curses
import time
from login import LOGIN_UI



# TODO: Solve responsiveness issues
def show_main_intro(stdscr):
    title1 = "**************************************************"
    title2 = "***  TERMEMAIL - TERMINAL BASED EMAIL CLIENT!  ***"
    title3 = "**************************************************"
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.A_BOLD)
    x_pos = w // 2 - (len(title1) // 2)
    y_pos = h // 2 - 1
    stdscr.addstr(y_pos, x_pos, title1)
    stdscr.refresh()
    time.sleep(0.15)
    x_pos = w // 2 - (len(title2) // 2)
    y_pos = h // 2
    stdscr.addstr(y_pos, x_pos, title2)
    stdscr.refresh()
    time.sleep(0.15)
    x_pos = w // 2 - (len(title3) // 2)
    y_pos = h // 2 + 1
    stdscr.addstr(y_pos, x_pos, title3)
    stdscr.refresh()
    time.sleep(0.15)
    stdscr.refresh()
    time.sleep(1)
    while y_pos < h - 3:
        stdscr.clear()
        y_pos += 2
        stdscr.addstr(y_pos - 1, x_pos,title1)
        stdscr.addstr(y_pos, x_pos, title2)
        stdscr.addstr(y_pos + 1, x_pos, title3)
        stdscr.refresh()
        if y_pos < h - 6:
            stdscr.attron(curses.A_DIM)
        time.sleep(0.035)
    stdscr.clear()
    stdscr.refresh()
    stdscr.attroff(curses.A_DIM)
    stdscr.attroff(curses.A_BOLD)



def main(stdscr):
    curses.curs_set(0)
    show_main_intro(stdscr)
    # TODO: Authenticate using file stored in directory
    LOGIN_UI(stdscr)



if __name__ == "__main__":
    curses.wrapper(main)