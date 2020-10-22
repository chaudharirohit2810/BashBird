import curses


class BottomBar:
    '''Class which shows bottom bar instructions

    Arguements \t
    stdscr: Standard screen attribute of curses \t
    options: Instructions to show in bottom bar. Should be array of dictionary with two keys as \t
    key(Key which needs pressed) and msg (instruction).
    '''


    #<!---------------------------------------------Variables--------------------------------------------->
    # Standard screen variable
    __stdscr = None

    # Options
    __options = []



    #<!---------------------------------------------Constructor-------------------------------------------------->
    def __init__(self, stdscr, options):
        self.__stdscr = stdscr
        self.__options = options
        self.__set_bottom_bar()



    #<!--------------------------------------------Private functions-------------------------------------------->
    
   
    def __set_bottom_bar(self):
        '''Setup bottom bar'''

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


   
    # Arguements:
    # y_pos = y_coordinate of instruction
    # x_pos = x_coordinate of instruction
    # key = Key which needs to be pressed
    # instruction = Title of instruction
    def __bottom_bar_instruction(self, y_pos, x_pos, key, instruction):
        '''Utility function which shows bottom bar instruction'''

        try:
            self.__stdscr.attron(curses.A_STANDOUT)
            self.__stdscr.addstr(y_pos, x_pos, key)
            self.__stdscr.attroff(curses.A_STANDOUT)
            self.__stdscr.attron(curses.A_BOLD)
            self.__stdscr.addstr(y_pos, x_pos + len(key) , instruction)
            self.__stdscr.attroff(curses.A_BOLD)
        except:
            return