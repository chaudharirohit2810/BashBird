import curses, textwrap, getpass, os
from IMAP.main import IMAP
from loading import Loading
from curses.textpad import rectangle
from BottomBar import BottomBar
from Title import Title
import utils

class EMAIL_INFO:

    #<!------------------------------------------------------Variables--------------------------------------------!>
    __subject = ""
    __from = ""
    __index = -1
    __body = ""
    __date = ""
    __is_error = False
    __is_attachment_present = False
    __attachment_data = None
    __attachment_filenames = []

    __imap = None
    __stdscr = None

    options = []

    #<!---------------------------------------------------Functions-----------------------------------------------!>
    '''Constructor of class'''
    # Arguements:
    # stdscr: Standard screen of curses
    # email_details: Touple containing index, subject, from and date respectively
    # imap: Imap object
    def __init__(self, stdscr, email_details, imap):

        # Initialize the variable
        self.__stdscr = stdscr
        self.__imap = imap
        self.options = [
            {'key': 'Q', 'msg': 'Go Back'}
        ]

        # Destructure the email_details
        self.__index, self.__subject, self.__from, self.__date = email_details
        self.__fetch_body(self.__index)

        if not self.__is_error:
            self.__main()


    #<!----------------------------------------------------Logic------------------------------------------------------>
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
                if key == curses.KEY_DOWN and start <= len(self.__body.splitlines()) - max_lines - 1:
                    start += 1
                elif key == curses.KEY_UP and start > 0:
                    start -= 1

            if self.__is_attachment_present and key == ord('d'):
                self.__download_attachment()


            max_lines = max(self.__set_main_layout(self.__body.splitlines()[start:]), max_lines)
            BottomBar(self.__stdscr, self.options)
            self.__stdscr.refresh()

            
    '''To fetch body of emails using imap object'''
    def __fetch_body(self, index):
        try:
            # start loading
            loading = Loading(self.__stdscr)
            loading.start()
            response = self.__imap.fetch_whole_body(self.__index)
            self.__body = response['body']
            self.__is_attachment_present = response['is_attachment']
            self.__attachment_filenames = response['filename']

            # If attachment is_present add it in options array
            if response['is_attachment']:
                self.options.insert(0, {'key': 'D', 'msg': 'Download Attachment'})
            loading.stop()
        except Exception as e:
            print(e)
            # To show the error message
            loading.stop()
            self.__is_error = True
            self.__show_message("Something went wrong! Press 'q' to go back")


    '''To download attachments in mail'''
    def __download_attachment(self):
        try:
            utils.show_status_message(stdscr=self.__stdscr, msg="Downloading File.....", isLoading=True)
            msg = self.__imap.download_attachment(self.__index)
            utils.show_status_message(self.__stdscr, msg, time_to_show=3.5)
        except:
            utils.show_status_message(self.__stdscr, "Downloading failed! Please try again!!", time_to_show=2)





    
    #<!--------------------------------------------------- UI ------------------------------------------------------>


    '''Function which sets up the whole layout of main page'''
    def __set_main_layout(self, body):
        from_start = 3
        from_block_total = 4
        subject_lines = 4
        attachment_block = 0
            
            
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

        # If attachment is present show the block for attachment
        if self.__is_attachment_present == True:
            attachment_block = 2
            attachment_start = from_start + from_block_total + subject_lines

            # Convert attachment array to string
            filename_string = "  ".join(name for name in self.__attachment_filenames)
            # Wrap the attachment
            attach_arr = wrapper.wrap(filename_string)

            # Show the attachments
            for item in attach_arr:
                self.__stdscr.addstr(attachment_start + attachment_block, 2, item)
                attachment_block += 1
            
            rectangle(self.__stdscr, attachment_start + 1, 0, attachment_start + attachment_block, w - 2)
            self.__stdscr.addstr(attachment_start + 1, 2, " Attachments: ")
            

        # Body part of UI
        body_start = from_start + from_block_total + subject_lines + attachment_block
        rectangle(self.__stdscr, body_start + 1, 0, h - 5, w - 1)
        self.__stdscr.addstr(body_start + 1, 2, " BODY ")

        # Divide body into parts
        
        max_lines = (h - 5) - (body_start + 1) - 2
        body_start += 2
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
        # return max number of lines
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

    
    
