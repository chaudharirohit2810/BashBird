import time
import curses
import sys
from write_mail import Write_Mail_UI

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


'''Utility Menu class which displays menu on screen'''
class Menu:

    # <-------------------------------------Variables------------------------------------>
    __curr_index = 0 # Current position in menu
    __stdscr = None # Stdscr variable of curses
    __menu = [] # Available menu options



    #<----------------------------------------Functions-------------------------------------->

    '''Constructor'''
    # Arguements:
    # stdscr: Stdscr of curses
    # menu_options: Options available for menu
    # TODO: For now just list of strings is arguements later take list of strings mapped with functions
    def __init__(self, stdscr, menu_options):
        curses.curs_set(0)
        
        self.__stdscr = stdscr
        self.__menu = menu_options
        self.__setup_color_pairs()
        self.__display_menu()
        while 1:
            key = self.__stdscr.getch()
        
            if key == curses.KEY_UP and self.__curr_index != 0:
                self.__curr_index -= 1
            elif key == curses.KEY_DOWN and self.__curr_index != len(self.__menu) - 1:
                self.__curr_index += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                self.__on_enter_pressed()
                continue
            
            self.__display_menu()





    #<-------------------------------------------Private Functions------------------------------------->

    '''Main function which displays menu'''    
    def __display_menu(self):
        # Get height and width of screen (Required for centering menu)
        h, w = self.__stdscr.getmaxyx()

        # Clear the screen
        self.__stdscr.clear()

        # Iterate over each option in menu
        for index, item in enumerate(self.__menu):

            # Determine the center position of menu
            x_pos = w // 2 - len(item['title']) // 2
            y_pos = h // 2 - len(self.__menu) // 2 + index

            # Check if index is of currently selected item if yes make its background white
            if self.__curr_index == index:
                self.__stdscr.attron(curses.color_pair(1))

            # Print string on screen
            self.__stdscr.addstr(y_pos, x_pos, item['title'])

            if self.__curr_index == index:
                self.__stdscr.attroff(curses.color_pair(1))
        
        # Refresh the screen
        self.__stdscr.refresh()



    '''When enter is pressed on particular item'''
    def __on_enter_pressed(self):
        # Last item should be exit which will close the program
        # TODO: It is just for temporary use, later we will remove it
        if self.__curr_index == len(self.__menu) - 1:
            sys.exit()

        # Call the desired function
        self.__menu[self.__curr_index]['Function'](self.__stdscr)


        self.__display_menu()



    #<--------------------------------------------Utility functions---------------------------------------->
    
    '''Function to setup color pairs required'''
    def __setup_color_pairs(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        


menu_strings = ["Show email", "Logout", "Exit"]
def main(stdscr):
    menu = [{'title': "Write mail", 'Function': Write_Mail_UI}]
    for item in menu_strings:
        # Alert: Function will expect first arguement as stdscr for sure
        menu.append({'title': item, 'Function': temp})
    Menu(stdscr, menu)

if __name__ == "__main__":
    curses.wrapper(main)