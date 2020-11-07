import curses
import time
import os
import getpass
import sys
from login import LOGIN_UI
from dotenv import load_dotenv
from IMAP.main import IMAP
from main_menu import Main_Menu
from get_credentials import Credentials


def createDirectory(dir_path):
    '''To create directory which stores configuration file'''

    try:
        os.mkdir(dir_path)
    except FileExistsError as e:
        pass
    except Exception as e:
        sys.exit()


def authenticate():
    '''To check if user is already logged in and authenticates according to it'''
    # TODO: Decode the email and password as they will be encrypted later
    cred = Credentials()
    flag, email, password = cred.get_credentials()
    if not flag:
        return flag
    # Check if email and password present in file
    if email != None and password != None:
        try:
            IMAP(email, password)
        except:
            # Credentials are invalid
            flag = False
    return flag


def show_main_intro(stdscr):
    '''To show the intro screen'''
    # TODO: Solve responsiveness issues

    title1 = "**************************************************"
    title2 = "***** TERMMAIL - TERMINAL BASED EMAIL CLIENT *****"
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
    flag = authenticate()
    if flag == False:
        time.sleep(0.5)
    while y_pos < h - 3:
        stdscr.clear()
        y_pos += 2
        stdscr.addstr(y_pos - 1, x_pos, title1)
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
    return flag


def main(stdscr):
    curses.curs_set(0)
    # Get username
    user = getpass.getuser()
    # Mail directory path
    dir_path = '/home/'+user+'/.termmail'
    createDirectory(dir_path)
    # Environment file
    env_path = dir_path + "/.env"
    load_dotenv(env_path)
    is_authenticated = show_main_intro(stdscr)
    # If the user is already authenticated then go to main menu
    if is_authenticated == True:
        Main_Menu(stdscr).show()
    # Else show the login page
    else:
        LOGIN_UI(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)
