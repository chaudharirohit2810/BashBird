import curses, os
import time, textwrap
from BottomBar import BottomBar
from loading import Loading
from dotenv import load_dotenv
from IMAP.main import IMAP
from Title import Title
from email_info import EMAIL_INFO


class EMAIL_LIST:

    #<!-------------------------------------------------Variables---------------------------------------------------!>
    __stdscr = None
    __directory_name = "" # Name of mailbox
    __is_error = False # Check if there is error
    __imap = None # To store imap variable

    __curr_position = 0
    __arr_position = 0
    num = 0
    emails = None
    exception = ""

    options = [
        {'key': 'D', 'msg': 'Delete Mail'},
        {'key': 'Q', 'msg': 'Go Back'},
        {'key': '⇵', 'msg': 'Navigate through emails'},
        {'key': '⏎', 'msg': 'To See Details'},
    ]

    __main_list = []

    #<!------------------------------------------------Functions-----------------------------------------------------!>
    '''Constructor of class'''
    # Arguements:
    # stdscr: Standard screen of curses
    # directory_name: Name of mailbox from which mails are fetched
    # imap: object of imap class
    def __init__(self, stdscr, directory_name, imap):
        # To disable cursor
        curses.curs_set(0)

        # Setup the variables
        self.__stdscr = stdscr
        self.__directory_name = directory_name
        self.__imap = imap

        # To fetch emails
        self.__fetch_emails()

        if not self.__is_error:
            # To setup bottom bar menu to show instructions
            self.__setup_bottom_bar()

            # To setup list of emails
            self.__set_main_layout()

            # Refresh the screen
            self.__stdscr.refresh()



    '''To fetch emails from imap server using IMAP class'''
    # TODO: Run this function in thread
    def __fetch_emails(self):
        try:
            # Start loading until mails are fetched
            loading = Loading(self.__stdscr)
            loading.start()
            
            # Select particular mailbox
            num = self.__imap.select_mailbox(self.__directory_name)

            self.num = num

            if num == 0:
                loading.stop()
                self.__is_error = True
                msg = "Nothing in " + self.__directory_name[1:-1] + "!! Press 'q' to go back"
                self.__show_message(msg)
                return
            
            # Fetch atleast 30 mails if total mails are less than that then fetch total number of mails
            count = min(num - 1, 30)

            emails = self.__imap.fetch_email_headers(num, count)

            # Check if the request was success
            # TODO: If the request failed then show the error message
            if emails[0]:
                self.__main_list = emails[1]
                self.emails = emails

            # Stop the loading
            loading.stop()

        except Exception as e:
            # To show the error message
            loading.stop()
            self.__is_error = True
            self.__show_message("Something went wrong! Press 'q' to go back")
            
            


    '''To setup the main layout of page with scrollable behaviour'''
    def __set_main_layout(self):


        key = 0
        arr_start = 0
        # Initially setup the list to get maximum mails that can be shown on single page
        max_len = self.__set_email_list(self.__main_list)

        # Loop until key is 'q'
        while key != ord('q'):
            key = self.__stdscr.getch()
            
            # If the key pressed is up
            if key == curses.KEY_UP and self.__arr_position != 0:
                self.__curr_position -= 1
                self.__arr_position -= 1

                # if the current position becomes -1 then show previous page.
                if self.__curr_position == -1:
                    arr_start = arr_start - max_len
                    self.__curr_position = max_len - 1

            # IF the key pressed is down
            elif key == curses.KEY_DOWN:
                if self.__arr_position != len(self.__main_list) - 1:
                    self.__curr_position += 1
                    self.__arr_position += 1

                    # It the current position becomes max_len then show next page.
                    if self.__curr_position >= max_len:
                        arr_start = self.__arr_position

                        # Again reset the current position
                        self.__curr_position = 0

            # When enter is pressed
            elif key == curses.KEY_ENTER or key in [10, 13]:
                # Show the email info component which will show details of email
                EMAIL_INFO(self.__stdscr, 
                            (self.num - self.__arr_position, self.__main_list[self.__arr_position]['Subject'], 
                            self.__main_list[self.__arr_position]['From'], self.__main_list[self.__arr_position]['Date']), 
                         self.__imap)
                    

            # Calculate the end of display list
            arr_end = min(arr_start + max_len, len(self.__main_list))

            # Show the email list
            max_len = max(self.__set_email_list(self.__main_list[arr_start:arr_end]), max_len)


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



            key = self.__stdscr.getch()

        
        



    '''To show the list of emails'''
    # Arguements:
    # list: List of emails
    def __set_email_list(self, list):

        # Get the height and width of standard screen
        h, w = self.__stdscr.getmaxyx()

        self.__stdscr.clear()

        # setup title
        title = "Emails in " + self.__directory_name
        Title(self.__stdscr, title)

        # Start of emali list
        start = 2
        i = 0

        # Loop over the list until the screen or list is ended
        while start < h - 5 and i < len(list):
            # Check if the list item is focused 
            is_focused = i == self.__curr_position

            # Show the email
            start = self.__set_mail_item(start, list[i]['Subject'],
                                         list[i]['From'],
                                         list[i]['Date'], h, w, is_focused=is_focused)
            i += 1

        # Setup the bottom bar as screen was cleared
        self.__setup_bottom_bar()

        # Refresh the layout
        self.__stdscr.refresh()

        # Return the total number of shown emails
        return i


    '''To show the single mail item'''
    # Arguements:
    # Subject: Subject of mail
    # mail_From: email of sender
    # data: Date of email
    # height, width: height and width of screen
    # is_focused: if the email item is focused or not
    # Returns the total height of mail item
    def __set_mail_item(self, start, subject, mail_from, date, height, width, is_focused=False):
        # Formate date and mail from
        mail_from = "From: " + mail_from
        formatted_date = "Date: " + date

        # if the mail item is focused then make that a bold
        # TODO: Use different method to focus email as bold need to used for non-read mails
        if is_focused:
            # subject = subject + "This is focused"
            self.__stdscr.attron(curses.A_BOLD)

        # Determine start x-position of date
        # TODO: Later also check the end of subject so date can be shifted to new line
        date_start = width - len(formatted_date) - 2

        if len(subject.strip()) == 0:
            subject = "(no subject)"
        
        # To show subject
        # First wrap the subject so that it can be shown on newline
        # self.__stdscr.attron(curses.A_BOLD)
        wrapper = textwrap.TextWrapper(width=width - 2)
        formatted_subject = wrapper.wrap(subject)
        for index, subject in enumerate(formatted_subject):
            flag = False
            # If there is more than 1 line 
            if index == 1:
                ellipsize = "...."
                sub_end = min(width - 15, len(subject))
                # Add ellipses when subject is huge 
                if sub_end != len(subject):
                    subject = subject[0:sub_end] + ellipsize
                    # Make flag true to break out of loop
                    flag = True
            self.__stdscr.addstr(start, 1, subject)
            start += 1
            if flag:
                break

        # To show mail from
        self.__stdscr.addstr(start, 1, mail_from)

        # To show date
        self.__stdscr.addstr(start, date_start, formatted_date)
        start += 1

        # To show horizontal line at the end of mail
        self.__stdscr.hline(start, 0, curses.ACS_HLINE, width)
        start += 1

        if is_focused:
            self.__stdscr.attroff(curses.A_BOLD)

        # Return the end of layout to show next email
        return start


    '''To setup bottom bar'''
    def __setup_bottom_bar(self):
        BottomBar(self.__stdscr, self.options)


def main(stdscr):
    EMAIL_LIST(stdscr, "INBOX", None)


if __name__ == "__main__":
    curses.wrapper(main)
