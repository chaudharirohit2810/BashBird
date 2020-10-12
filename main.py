import curses
import time, os
from login import LOGIN_UI
from dotenv import load_dotenv
from SMTP.main import SEND_MAIL
from main_menu import Main_Menu

'''To check if user is already logged in and authenticates according to it'''
# TODO: Decode the email and password as they will be encrypted later
def authenticate():
    flag=False
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    # Check if email and password present in file
    if email != None and password != None:
        try:
            SEND_MAIL(email, password)
            flag = True
        except:
            pass
    return flag


'''To show the intro screen'''
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
    flag = authenticate()
    if flag == False:
        time.sleep(0.5)
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
    return flag



def main(stdscr):
    curses.curs_set(0)
    load_dotenv('./.env')
    is_authenticated = show_main_intro(stdscr)
    # If the user is already authenticated then go to main menu
    if is_authenticated == True:
        Main_Menu(stdscr).show()
    # Else show the login page
    else:
        LOGIN_UI(stdscr)



if __name__ == "__main__":
    curses.wrapper(main)