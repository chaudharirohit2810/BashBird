from menu import Menu
import curses
import os
import getpass
import sys
from write_mail import Write_Mail_UI
from show_folders import Show_Folders
from curses.textpad import rectangle
from get_credentials import Credentials


class Main_Menu:
    '''Class which shows main menu

        Arguements \t
        stdscr: Standard screen

    '''

    # <!---------------------------------------------------Variables------------------------------------------------>
    __menu_strings = ["Exit"]
    __menu = []
    __stdscr = None
    # Confirm Email Variables
    __curr_confirm_index = 0
    __confirm_menu = ["YES", "NO"]

    # <!-------------------------------------------------Functions--------------------------------------------------->

    def __init__(self, stdscr):
        self.__stdscr = stdscr
        menu = [{'title': "Write mail", 'Function': Write_Mail_UI, 'args': None}]
        menu.append(
            {'title': "View mails", 'Function': Show_Folders, 'args': None})
        menu.append(
            {'title': "Logout", 'Function': self.__set_confirm_email_bar, 'args': "STDSCR_NR"})
        for item in self.__menu_strings:
            # Alert: Function will expect first arguement as stdscr for sure
            menu.append({'title': item, 'Function': None, 'args': None})
        self.__menu = menu

    def __display_bottom_bar_menu(self):
        '''To display UI of confirm email bottom bar for logout'''

        h, _ = self.__stdscr.getmaxyx()

        start_h = h - 3
        for index, item in enumerate(self.__confirm_menu):

            y_pos = start_h + index
            # Check if index is of currently selected item if yes make its background white
            if self.__curr_confirm_index == index:
                self.__stdscr.attron(curses.color_pair(1))

            # Print string on screen
            self.__stdscr.addstr(y_pos, 2, item)

            if self.__curr_confirm_index == index:
                self.__stdscr.attroff(curses.color_pair(1))

        self.__stdscr.refresh()

    def __set_confirm_email_bar(self):
        '''Setup confirm email bar for logout'''

        h, w = self.__stdscr.getmaxyx()
        title = " Do you want to logout ".upper()
        rectangle(self.__stdscr, h - 4, 0, h - 1, w - 2)
        self.__stdscr.attron(curses.A_BOLD)
        self.__stdscr.addstr(h - 4, 1, title)
        self.__stdscr.attroff(curses.A_BOLD)
        self.__display_bottom_bar_menu()

        while 1:
            key = self.__stdscr.getch()

            if key == curses.KEY_UP and self.__curr_confirm_index != 0:
                self.__curr_confirm_index -= 1
            elif key == curses.KEY_DOWN and self.__curr_confirm_index != len(self.__confirm_menu) - 1:
                self.__curr_confirm_index += 1

            # TODO: Do the functionality according to choice of user
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.__curr_confirm_index == 0:
                    # Remove the .env file
                    # Get the environment filepath
                    user = getpass.getuser()
                    cred = Credentials()
                    cred.remote_credentials()
                    sys.exit()
                break

            self.__display_bottom_bar_menu()

    def show(self):
        '''To show the menu'''

        Menu(self.__stdscr, self.__menu, "Main menu", isMain=True)
