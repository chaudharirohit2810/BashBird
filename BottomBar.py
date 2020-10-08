import curses

'''Class which shows bottom bar instructions'''
class BottomBar:

    #<!---------------------------------------------Variables--------------------------------------------->
    # Standard screen variable
    __stdscr = None

    # Options
    __options = []



    #<!---------------------------------------------Constructor-------------------------------------------------->
    '''Constructor'''
    # Arguements:
    # stdscr: Standard screen attribute of curses
    # options: Instructions to show in bottom bar. Should be array of dictionary with two keys as 
    #          key(Key which needs pressed) and msg (instruction).
    def __init__(self, stdscr, options):
        self.__stdscr = stdscr
        self.__options = options
        self.__set_bottom_bar()



    #<!--------------------------------------------Private functions-------------------------------------------->
    
    '''Setup bottom bar'''
    # TODO: Later need to change this to use array and setup the length and width of bottom bar accordingly
    # TODO: Major changes required
    # TODO: Use array for displaying the functions
    # Alert: Looks like there are still lots of bugs 
    def __set_bottom_bar(self):
        h, w = self.__stdscr.getmaxyx()
        # To show horizontal line
        self.__stdscr.hline(h - 4, 0, curses.ACS_HLINE, w)

        # Loop which shows all the options
        x_start = 1
        for index, item in enumerate(self.__options):
            start = h - 3
            if index % 2 == 1: 
                start = h - 2
            self.__bottom_bar_instruction(start, x_start, " " + item['key'] + ":", " " + item['msg'])
            if index % 2 == 1:
                x_start += 30


    '''Utility function which shows bottom bar instruction'''
    # Arguements:
    # y_pos = y_coordinate of instruction
    # x_pos = x_coordinate of instruction
    # key = Key which needs to be pressed
    # instruction = Title of instruction
    def __bottom_bar_instruction(self, y_pos, x_pos, key, instruction):
        try:
            self.__stdscr.attron(curses.A_STANDOUT)
            self.__stdscr.addstr(y_pos, x_pos, key)
            self.__stdscr.attroff(curses.A_STANDOUT)
            self.__stdscr.attron(curses.A_BOLD)
            self.__stdscr.addstr(y_pos, x_pos + len(key) , instruction)
            self.__stdscr.attroff(curses.A_BOLD)
        except:
            return