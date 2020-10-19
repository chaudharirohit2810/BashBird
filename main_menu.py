from menu import Menu
import curses, os, getpass, sys
from write_mail import Write_Mail_UI
from show_folders import Show_Folders
from curses.textpad import rectangle



'''Main menu class which shows main menu'''
class Main_Menu:
    __menu_strings = [ "Exit"]
    __menu = []
    __stdscr = None
    #Confirm Email Variables
    __curr_confirm_index = 0
    # TODO: Later changes this array to title and function dictionary
    __confirm_menu =["YES", "NO"]


    '''Constructor of main menu'''
    # Arguements
    # stdscr    Standard screen
    def __init__(self, stdscr):
        self.__stdscr = stdscr
        menu = [{'title': "Write mail", 'Function': Write_Mail_UI, 'args': None}]
        menu.append({'title': "View mails", 'Function': Show_Folders, 'args': None})
        menu.append({'title': "Logout", 'Function': self.__set_confirm_email_bar, 'args': "STDSCR_NR"})
        for item in self.__menu_strings:
            # Alert: Function will expect first arguement as stdscr for sure
            menu.append({'title': item, 'Function': None, 'args': None})
        self.__menu = menu
    


    '''To display confirm email bottom bar'''
    # TODO: Later get title and functionality in array (for now only title is present)
    def __display_bottom_bar_menu(self):
        h, w = self.__stdscr.getmaxyx()
        
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

    
    '''Setup confirm email bar'''
    def __set_confirm_email_bar(self):
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
                    dir_path = '/home/'+user+'/.termmail'
                    env_path = dir_path + "/.env"
                    os.remove(env_path)
                    sys.exit()
                    
                break

            self.__display_bottom_bar_menu()




    
    
    '''To show the menu'''
    def show(self):
        Menu(self.__stdscr, self.__menu, "Main menu", isMain=True)