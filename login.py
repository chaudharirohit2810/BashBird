import curses
import time
import sys
import getpass
from curses.textpad import rectangle, Textbox
from BottomBar import BottomBar
from SMTP.main import SMTP
from threading import Thread
from main_menu import Main_Menu
from login_instructions import Instructions
import utils
from get_credentials import Credentials


class LOGIN_UI:
    '''Class which shows login screen

        Arguements \t
        stdscr: Standard screen of curses

    '''

    # <!------------------------------------------Variables------------------------------------------------->
    __stdscr = None
    __x_start = 0
    __x_end = 0
    __y_start = 0
    __nol = 1
    __noc = 40
    __height = 1
    __width = 1
    __y_end = 0

    # options for bottom bar which shows all the instructions to follow
    __options = [
        {'key': 'e', 'msg': 'Edit email'},
        {'key': 'p', 'msg': 'Enter password'},
        {'key': 'l', 'msg': 'Login'},
        {'key': 'q', 'msg': 'Exit'},
        {'key': 'i', 'msg': 'Show Login Instructions'}
    ]

    # <!----------------------------------------------------Functions-------------------------------------->
    def __init__(self, stdscr):
        self.__stdscr = stdscr
        self.__set_values()
        self.__main()

    # Arguements:
    # email: Default email to show
    # password: Pasword to show
    # isEdit: If none don't show save message else show save message based on True or False value

    def __setup_layout(self, email, password, isEdit=None):
        '''To set the default layout of login screen'''

        self.__stdscr.clear()
        utils.set_title(self.__stdscr, "LOGIN")
        # Setting up title and padding rectangle
        rectangle(self.__stdscr, self.__y_start - 3,
                  self.__x_start - 4, self.__y_end, self.__x_end + 6)
        title = " Login to your account ".upper()
        self.__stdscr.attron(curses.A_BOLD)
        self.__stdscr.addstr(self.__y_start - 3,
                             self.__width // 2 - len(title) // 2 + 1, title)
        self.__stdscr.attroff(curses.A_BOLD)

        # Setting up view of email textbox
        self.__stdscr.attron(curses.A_BOLD)
        rectangle(self.__stdscr, self.__y_start, self.__x_start,
                  self.__y_start + self.__nol + 1, self.__x_end + 2)
        email_msg = " Email: "
        if isEdit == False:
            email_msg += "(Ctrl + G to save) "
        self.__stdscr.addstr(self.__y_start, self.__x_start + 1, email_msg)

        # Setting up view of password textbox
        # TODO: Later add asterisk to editbox
        pass_start = self.__y_start + self.__nol + 3
        rectangle(self.__stdscr, pass_start, self.__x_start,
                  pass_start + self.__nol + 1, self.__x_end + 2)
        password_msg = " Password: "
        if isEdit == True:
            password_msg += "(Ctrl + G to save) "
        self.__stdscr.addstr(pass_start, self.__x_start + 1, password_msg)
        self.__stdscr.attroff(curses.A_BOLD)

        # Add the email and password on screen
        self.__stdscr.addstr(self.__y_start + 1, self.__x_start + 2, email)
        self.__stdscr.addstr(self.__y_start + 5, self.__x_start + 2, password)

        # setup bottom bar
        BottomBar(self.__stdscr, self.__options)

        self.__stdscr.refresh()

    def __edit_box(self, email, password, posy, posx, isPass=False):
        '''Edit box for login and password'''

        # TODO: Use isPass to show asterisk for password
        nol = 1
        noc = 40
        editwin = curses.newwin(nol, noc, posy, posx)
        self.__setup_layout(email, password, isPass)

        if isPass:

            ch = self.__stdscr.getch()
            password = password
            password_asterisk = "*" * len(password)
            editwin.insstr(password_asterisk)
            while ch != curses.ascii.BEL:
                if ch == curses.KEY_BACKSPACE:
                    try:
                        password = password[:-1]
                    except:
                        pass
                elif ch >= 32 and ch <= 127:
                    password += chr(ch)
                password_asterisk = "*" * len(password)

                editwin.clear()
                editwin.insstr(password_asterisk)
                editwin.refresh()
                ch = self.__stdscr.getch()
            curses.curs_set(0)
            return password
        else:
            curses.curs_set(1)
            editwin.insstr(email)
            editwin.refresh()
            box_email = Textbox(editwin)
            box_email.stripspaces = True
            box_email.edit()
            curses.curs_set(0)
            return box_email.gather()

    def __main(self):
        '''Main function which setups the whole login page'''

        curses.curs_set(0)
        self.__setup_layout("", "")
        key = 1
        email = ""
        password = ""
        utils.set_title(self.__stdscr, "LOGIN")
        utils.show_status_message(
            self.__stdscr, "Please read login instructions before logging in!!", time_to_show=2)
        while key != ord('q'):
            # If the key is e then make the email box active
            if key == ord('e'):
                email = self.__edit_box(
                    email, "*" * len(password), self.__y_start + 1, self.__x_start + 2)

            # If the key is p then make the password box active
            elif key == ord('p'):
                password = self.__edit_box(
                    email, "*" * len(password), self.__y_start + 5, self.__x_start + 2, isPass=True)

            elif key == ord('l'):
                # Authenticate
                self.__authenticate(email, password)

            # Show login instructions
            elif key == ord('i'):
                Instructions(self.__stdscr)

            # This is to refresh the layout when user resizes the terminal
            self.__set_values()
            self.__setup_layout(email, "*" * len(password))

            self.__stdscr.refresh()
            key = self.__stdscr.getch()
        sys.exit()

    # Arguements:
    # email: Email of user
    # password: Password of user

    def __authenticate(self, email, password):
        '''To Authenticate using SMTP Server'''

        # Show the authenticating message
        utils.show_status_message(
            self.__stdscr, "Authenticating....", isLoading=True)
        try:
            self.__is_valid(email, password)
            # Authenticate using email and password, it throws exception if something went wrong
            SMTP(email, password)
            # Store in .termmail directory
            cred = Credentials()
            cred.store_credentials(email, password)
            utils.show_status_message(
                self.__stdscr, "Authentication Successful", time_to_show=1)
            # Show main menu after authentication is completed
            main_menu = Main_Menu(self.__stdscr)
            main_menu.show()

        except Exception as e:
            utils.show_status_message(self.__stdscr, str(e), time_to_show=3)

    # Arguements:
    # email : Email of user
    # password: Password of user

    def __store_in_file(self, email, password):
        '''To store email and password in separate file'''

    # <!------------------------------------------------Utils------------------------------------------------->
    def __is_valid(self, email, password):
        '''Check if email and password are valid'''

        if len(email.strip()) == 0 or len(password.strip()) == 0:
            raise Exception("Please enter valid email and password")

    '''To setup the default values'''

    def __set_values(self):

        # Set the value of height and width
        self.__height, self.__width = self.__stdscr.getmaxyx()

        # Starting x-coordinate
        self.__x_start = self.__width // 2 - self.__noc // 2

        # Ending x-coordinate
        self.__x_end = self.__width // 2 + self.__noc // 2

        # Starting y-coordinate
        self.__y_start = self.__height // 2 - 3

        # Ending y-coordinate
        self.__y_end = self.__y_start + 9


def main(stdscr):
    LOGIN_UI(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)
