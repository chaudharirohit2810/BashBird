import curses, textwrap
from IMAP.main import IMAP
from loading import Loading
from curses.textpad import rectangle
from BottomBar import BottomBar
from Title import Title

class EMAIL_INFO:

    #<!------------------------------------------------------Variables--------------------------------------------!>
    __subject = ""
    __from = ""
    __body = ""
    __date = ""
    __is_error = False

    __imap = None
    __stdscr = None

    options = [
        {'key': 'D', 'msg': 'Delete Mail'},
        {'key': 'Q', 'msg': 'Go Back'}
    ]

    #<!---------------------------------------------------Functions-----------------------------------------------!>

    def __init__(self, stdscr, email_details, imap):

        # Initialize the variable
        self.__stdscr = stdscr
        self.__imap = imap

        # Destructure the email_details
        index, self.__subject, self.__from, self.__date = email_details
        self.__fetch_body(index)

        if not self.__is_error:
            self.__main()

    
    '''Main wrapper function'''
    def __main(self):
        key = 0
        start = 0
        curses.curs_set(0)
        max_lines = self.__set_main_layout(self.__body.splitlines()[start:])
        BottomBar(self.__stdscr, self.options)
        while key != ord('q'):
            
            key = self.__stdscr.getch()

            flag = False

            if len(self.__body.splitlines()) < max_lines:
                flag = True

            if not flag:
                if key == curses.KEY_DOWN and start <= len(self.__body.splitlines()) - max_lines - 3:
                    start += 1
                elif key == curses.KEY_UP and start > 0:
                    start -= 1

            max_lines = max(self.__set_main_layout(self.__body.splitlines()[start:]), max_lines)
            BottomBar(self.__stdscr, self.options)
            self.__stdscr.refresh()

            


    
    def __fetch_body(self, index):
        try:
            loading = Loading(self.__stdscr)
            loading.start()
            self.__body = self.__imap.fetch_whole_body(index)
            loading.stop()
        except Exception as e:
            print(e)
            # To show the error message
            loading.stop()
            self.__is_error = True
            self.__show_message("Something went wrong! Press 'q' to go back")

    

    '''Function which sets up the whole layout of main page'''
    def __set_main_layout(self, body):
        from_start = 3
        from_block_total = 4
        subject_lines = 4
            
            
        h, w = self.__stdscr.getmaxyx()
        self.__stdscr.clear()
        Title(self.__stdscr, "Email Information")

        # From, To part of UI
        self.__stdscr.addstr(from_start, 1, "From: " + self.__from)
        rectangle(self.__stdscr, from_start - 1, 0, from_start + 1, w - 1)

        self.__stdscr.addstr(from_start + 2, 1, "Date: " + self.__date)
        rectangle(self.__stdscr, from_start - 1, 0, from_start + 3, w - 1)

        # Subject part of UI
        rectangle(self.__stdscr, from_start + from_block_total, 0, from_start + from_block_total + subject_lines, w - 1)
        self.__stdscr.addstr(from_start + from_block_total, 2, " SUBJECT ")

        if len(self.__subject.strip()) == 0:
            self.__subject = "(no subject)"

        # used to divide subject in multiple lines
        wrapper = textwrap.TextWrapper(width=w - 3)
        elipsize = "....."
        subject_arr = wrapper.wrap(self.__subject)
        # show the wrapped text
        for index, subject in enumerate(subject_arr):
            if index == 2:
                # If there are more than 3 lines then add elipsize
                subject = subject[0:w - 10] + elipsize
                self.__stdscr.addstr(from_start + from_block_total + 1 + index, 1, subject)
                break
            self.__stdscr.addstr(from_start + from_block_total + 1 + index, 1, subject)
            

        # Body part of UI
        rectangle(self.__stdscr, from_block_total + from_start + subject_lines + 1, 0, h - 5, w - 1)
        self.__stdscr.addstr(from_block_total + from_start + subject_lines + 1, 2, " BODY ")

        # Divide body into parts
        body_start = 13
        max_lines = (h - 5) - (from_block_total + from_start + subject_lines + 1) - 2
        body_end = body_start + max_lines
        for item in body:
            body_arr = wrapper.wrap(item)
            if body_start > body_end:
                break
            for body in body_arr:
                # ellipsize the text if it can't be fit into the box
                if body_start > body_end:
                    break
                self.__stdscr.addstr(body_start, 1, body)
                body_start += 1

        return max_lines



    '''To show message when mailbox is empty or some error occured'''
    def __show_message(self, msg):
        h, w = self.__stdscr.getmaxyx()
        
        key = 0
        while key != ord('q'):
            # Clear the screen
            self.__stdscr.clear()
             
            self.__stdscr.attron(curses.A_BOLD)
            self.__stdscr.addstr(h // 2, w // 2 - len(msg) // 2, msg)
            self.__stdscr.attroff(curses.A_BOLD)

            # Refresh the screen
            self.__stdscr.refresh()

            # Get user input from user
            key = self.__stdscr.getch()