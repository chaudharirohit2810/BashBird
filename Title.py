import curses

'''Show title of page'''
class Title:

    __stdscr = None

    def __init__(self, stdscr, title):
        self.__stdscr = stdscr
        self.__set_title(title)


    '''Setup Title on Top'''
    # TODO: Set background and foreground color of title to different color
    # TODO: Try different combinations of color
    def __set_title(self, title):
        _, w = self.__stdscr.getmaxyx()

        # Procedure followed to set title at the center and to set background as white
        count = w // 2 - len(title) // 2
        temp_title = ""
        for i in range(count):
            temp_title += " "
        temp_title += title.upper()
        for i in range(count - 1):
            temp_title += " "

        # Print the title
        self.__stdscr.attron(curses.A_STANDOUT)
        self.__stdscr.attron(curses.A_BOLD)
        self.__stdscr.addstr(0, 0, temp_title)
        self.__stdscr.attroff(curses.A_BOLD)
        self.__stdscr.attroff(curses.A_STANDOUT)

        self.__stdscr.refresh()