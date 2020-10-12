from menu import Menu
import curses
from write_mail import Write_Mail_UI
from show_folders import Show_Folders

'''Temporary function to check if passing function to dictionary is working'''
def temp(stdscr):
    # Get height and width of screen
    h, w = stdscr.getmaxyx()

    # Print that particular item at center of screen
    stdscr.clear()
    msg = "You entered into temporary  mode!"
    x_pos = w // 2 - len(msg) // 2
    y_pos = h // 2
    stdscr.addstr(y_pos, x_pos, msg)
    stdscr.refresh()

    # If backspace is pressed go back to menu
    # TODO: Later will need to switch this to some other key
    key = stdscr.getch()

    # While key is not backspace take input from user
    # TODO: Later delete this might cause problem
    while key != curses.KEY_BACKSPACE:
        key = stdscr.getch()


'''Main menu class which shows main menu'''
class Main_Menu:
    __menu_strings = [ "Logout", "Exit"]
    __menu = []
    __stdscr = None
    '''Constructor of main menu'''
    # Arguements
    # stdscr    Standard screen
    def __init__(self, stdscr):
        self.__stdscr = stdscr
        menu = [{'title': "Write mail", 'Function': Write_Mail_UI, 'args': None}]
        menu.append({'title': "View mails", 'Function': Show_Folders, 'args': None})
        for item in self.__menu_strings:
            # Alert: Function will expect first arguement as stdscr for sure
            menu.append({'title': item, 'Function': temp, 'args': None})
        self.__menu = menu
    
    
    '''To show the menu'''
    def show(self):
        Menu(self.__stdscr, self.__menu, "Main menu", isMain=True)