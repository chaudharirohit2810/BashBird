import curses, time


'''To show status message while authenticating'''
# Arguements:
# stdscr: Standard screen of curses
# msg: Message to show
# time_to_show: Time for which message needs to be shown
# isLoading: If the text is related to loading
 # TODO: Implement loading also
def show_status_message(stdscr, msg, time_to_show = -1, isLoading=False):
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