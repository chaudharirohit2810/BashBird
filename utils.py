import curses, time



def show_status_message(stdscr, msg, time_to_show = -1, isLoading=False):
    '''To show status message while authenticating
    
    Arguements \t
    stdscr: Standard screen of curses \t
    msg: Message to show \t
    time_to_show: Time for which message needs to be shown \t
    isLoading: To show loading animation \t

    '''

    h, w = stdscr.getmaxyx()
    # Blink the text if it is in loading state
    if isLoading:
        stdscr.attron(curses.A_BLINK)
    stdscr.attron(curses.A_STANDOUT)
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(h - 5, w // 2 - len(msg) // 2, " " + str(msg) +  " ")
    stdscr.refresh()
    if time_to_show != -1:
        time.sleep(time_to_show)
    # Disable attributes
    stdscr.attroff(curses.A_STANDOUT)
    stdscr.attroff(curses.A_BOLD)
    if isLoading:
        stdscr.attroff(curses.A_BLINK)

def show_message(stdscr, msg):
    '''To show message when mailbox is empty or some error occured

        Arguements \t
        stdscr: Standard screen of curses \t
        msg: Message to show \t
    '''

    h, w = stdscr.getmaxyx()
    
    key = 0
    while key != ord('q'):
        # Clear the screen
        stdscr.clear()
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(h // 2, w // 2 - len(msg) // 2, msg)
        stdscr.attroff(curses.A_BOLD)
        # Refresh the screen
        stdscr.refresh()
        key = stdscr.getch()



def set_title(stdscr, title):
    '''Show title of page

        Arguements \t
        stdscr: Standard screen of curses \t
        msg: title of page \t
    '''

    _, w = stdscr.getmaxyx()
    # Procedure followed to set title at the center and to set background as white
    count = w // 2 - len(title) // 2
    temp_title = ""

    for _ in range(count):
        temp_title += " "

    temp_title += title.upper()

    for _ in range(count - 1):
        temp_title += " "

    # Print the title
    stdscr.attron(curses.A_STANDOUT)
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(0, 0, temp_title)
    stdscr.attroff(curses.A_BOLD)
    stdscr.attroff(curses.A_STANDOUT)
    stdscr.refresh()