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
    __menu_strings = ["Logout", "Exit"]
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
        for item in self.__menu_strings:
            menu.append({'title': item, 'Function': None, 'args': None})
        self.__menu = menu

    def show(self):
        '''To show the menu'''

        Menu(self.__stdscr, self.__menu, "Main menu", isMain=True)
