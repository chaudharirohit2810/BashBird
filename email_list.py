import curses
import os
import time
import textwrap
from BottomBar import BottomBar
from loading import Loading
from dotenv import load_dotenv
from IMAP.main import IMAP
from email_info import EMAIL_INFO
from threading import Thread
from curses.textpad import rectangle
from threading import Thread
import utils


class EMAIL_LIST:
    '''To show list of emails

    Arguements \t
    stdscr: Standard screen of curses \t
    directory_name: Name of mailbox from which mails are fetched \t
    imap: object of imap class 

    '''

    # <!-------------------------------------------------Variables---------------------------------------------------!>
    __stdscr = None
    __directory_name = ""  # Name of mailbox
    __is_error = False  # Check if there is error
    __imap = None  # To store imap variable

    __curr_position = 0
    __arr_position = 0
    __num = 0
    __fetched_emails = 0
    __max_len = 20
    __delete_offset = 0
    __is_end = False

    options = [
        {'key': 'd', 'msg': 'Delete Mail'},
        {'key': 'q', 'msg': 'Go Back'},
        {'key': '⇵', 'msg': 'Navigate through emails'},
        {'key': '⏎', 'msg': 'To See Details'},
        {'key': 'l', 'msg': "Load next 50 emails"}
    ]

    __main_list = []
    __display_list = []
    emails = []

    # Confirm Email Variables
    __curr_confirm_index = 0
    # TODO: Later changes this array to title and function dictionary
    __confirm_menu = ["YES", "NO"]

    # Check if emails are getting fetched in separate thread
    __is_fetching_emails = True

    # <!------------------------------------------------Functions-----------------------------------------------------!>

    def __init__(self, stdscr, directory_name, imap):
        # To disable cursor
        curses.curs_set(0)

        # Setup the variables
        self.__stdscr = stdscr
        self.__directory_name = directory_name
        self.__imap = imap

        self.main()

    # <!----------------------------------------------- LOGIC -------------------------------------------------------->

    def main(self):
        # To fetch emails
        self.__fetch_emails()

        if not self.__is_error:
            # To setup bottom bar menu to show instructions
            self.__setup_bottom_bar()

            # To setup list of emails
            self.__set_main_layout()

            # Refresh the screen
            self.__stdscr.refresh()

    def __fetch_emails(self):
        '''To fetch emails from imap server using IMAP class'''

        try:
            # Start loading until mails are fetched
            loading = Loading(self.__stdscr)
            loading.start()
            # Select particular mailbox
            num = self.__imap.select_mailbox(self.__directory_name)

            if num == 0:
                loading.stop()
                self.__is_error = True
                msg = "Nothing in " + \
                    self.__directory_name.replace(
                        '"', '') + "!! Press 'q' to go back"
                utils.show_message(self.__stdscr, msg)
                return
            self.__num = num

            # Fetch atleast 50 mails if total mails are less than that then fetch total number of mails
            count = min(self.__num - 1, 50)
            if (self.__num - self.__fetched_emails) > 1:
                emails = self.__imap.fetch_email_headers(
                    self.__num - self.__fetched_emails, count)
                self.__delete_offset = self.__fetched_emails
                self.__fetched_emails += count + 1
                self.__main_list = emails
                self.__curr_position = 0
                self.__arr_position = 0
                self.__max_len = 0
                self.emails = emails
            else:
                self.__is_end = True

            loading.stop()
        except Exception as e:
            # To show the error message
            loading.stop()
            self.__is_error = True
            msg = "Something went wrong! Press 'q' to go back"
            utils.show_message(
                self.__stdscr, msg)

    def __set_main_layout(self):
        '''To setup the main layout of page with scrollable behaviour'''

        try:
            key = 0
            arr_start = 0
            # Initially setup the list to get maximum mails that can be shown on single page
            self.__display_list = self.__main_list
            self.__max_len = self.__set_email_list()

            # Show the message if there are no more mails fetched
            if self.__is_end:
                utils.show_status_message(
                    self.__stdscr, "No more mails available to fetch!!", time_to_show=2)
                self.__is_end = False

            # Loop until key is 'q'
            while key != ord('q'):
                key = self.__stdscr.getch()

                # If the key pressed is up
                if key == curses.KEY_UP and self.__arr_position != 0:
                    self.__curr_position -= 1
                    self.__arr_position -= 1

                    # if the current position becomes -1 then show previous page.
                    if self.__curr_position == -1:
                        arr_start = arr_start - self.__max_len
                        self.__curr_position = self.__max_len - 1

                # IF the key pressed is down
                elif key == curses.KEY_DOWN:
                    if self.__arr_position != len(self.__main_list) - 1:
                        self.__curr_position += 1
                        self.__arr_position += 1

                        # It the current position becomes max_len then show next page.
                        if self.__curr_position >= self.__max_len:
                            arr_start = self.__arr_position

                            # Again reset the current position
                            self.__curr_position = 0

                # If d is pressed
                elif key == ord('d'):
                    self.__set_confirm_email_bar()

                # Load next 50 emails
                elif key == ord('l'):
                    self.main()
                    break

                # When enter is pressed
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    # Show the email info component which will show details of email
                    EMAIL_INFO(self.__stdscr,
                               (self.__num - self.__arr_position - self.__delete_offset, self.__main_list[self.__arr_position]['Subject'],
                                self.__main_list[self.__arr_position]['From'], self.__main_list[self.__arr_position]['Date']),
                               self.__imap)

                # Calculate the end of display list
                arr_end = min(arr_start + self.__max_len,
                              len(self.__main_list))

                # Show the email list
                self.__display_list = self.__main_list[arr_start:arr_end]
                self.__max_len = max(self.__set_email_list(), self.__max_len)

        except Exception as e:
            msg = "Something went wrong! Press 'q' to go back"
            utils.show_message(
                self.__stdscr, msg)

    # <!-------------------------------------------------EMAIL LIST UI --------------------------------------------->

    # Arguements:
    # list: List of emails
    # isConfirm: If the bottom bar is confirm bottom bar menu or not

    def __set_email_list(self, isConfirm=False):
        '''To show the list of emails'''

        try:
            # Get the height and width of standard screen
            h, w = self.__stdscr.getmaxyx()

            self.__stdscr.clear()

            # setup title
            title = "Emails in " + self.__directory_name
            utils.set_title(self.__stdscr, title)

            # Start of emali list
            start = 2
            i = 0

            # Loop over the list until the screen or list is ended
            while start < h - 5 and i < len(self.__display_list):
                # Check if the list item is focused
                is_focused = i == self.__curr_position

                # Show the email
                start = self.__set_mail_item(start, self.__display_list[i]['Subject'],
                                             self.__display_list[i]['From'],
                                             self.__display_list[i]['Date'], h, w, is_focused=is_focused)
                i += 1

            # Setup the confirm email bottom menu if isConfirm is True
            if isConfirm:
                rectangle(self.__stdscr, h - 4, 0, h - 1, w - 2)
                title = " Do you want to delete email? ".upper()
                self.__stdscr.attron(curses.A_BOLD)
                self.__stdscr.addstr(h - 4, 1, title)
                self.__stdscr.attroff(curses.A_BOLD)
                self.__display_confirm_bottom_bar_menu()
            else:
                # Setup the bottom bar as screen was cleared
                self.__setup_bottom_bar()

            # Refresh the layout
            self.__stdscr.refresh()

            # Return the total number of shown emails
            return i
        except:
            utils.show_message(
                self.__stdscr, "Something went wrong! Press 'q' to go back")

    # Arguements:
    # Subject: Subject of mail
    # mail_From: email of sender
    # data: Date of email
    # height, width: height and width of screen
    # is_focused: if the email item is focused or not
    # Returns the total height of mail item

    def __set_mail_item(self, start, subject, mail_from, date, height, width, is_focused=False, is_seen=False):
        '''To show the single mail item'''
        curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        if is_focused:
            self.__stdscr.attron(curses.color_pair(10))
            self.__stdscr.attron(curses.A_BOLD)

        # Formate date and mail from
        mail_from = "From: " + mail_from
        formatted_date = "Date: " + date

        # if the mail item is focused then make that a bold
        # TODO: Use different method to focus email as bold need to used for non-read mails
        # if is_focused:
        #     # subject = subject + "This is focused"
        #     self.__stdscr.attron(curses.A_BOLD)

        old_start = start - 1

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
            self.__stdscr.attroff(curses.color_pair(10))
            rectangle(self.__stdscr, old_start, 0, start - 1, width - 1)
            self.__stdscr.attroff(curses.A_BOLD)

        # Return the end of layout to show next email
        return start

    def __set_confirm_email_bar(self):
        '''Setup confirm email bar'''

        try:
            h, w = self.__stdscr.getmaxyx()
            self.__stdscr.clear()
            self.__set_email_list(isConfirm=True)

            while 1:
                key = self.__stdscr.getch()

                if key == curses.KEY_UP and self.__curr_confirm_index != 0:
                    self.__curr_confirm_index -= 1
                elif key == curses.KEY_DOWN and self.__curr_confirm_index != len(self.__confirm_menu) - 1:
                    self.__curr_confirm_index += 1

                # TODO: Do the functionality according to choice of user
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    if self.__curr_confirm_index == 0:
                        utils.show_status_message(
                            self.__stdscr, "Deleting email....", isLoading=True)
                        try:
                            num = self.__imap.delete_email(
                                self.__num - self.__arr_position - self.__delete_offset)

                            # Set the new mail count
                            self.__num = num

                            # Update the array
                            self.__main_list.pop(self.__arr_position)

                            # Show mail sent successfully message
                            utils.show_status_message(
                                self.__stdscr, "Mail deleted Successfully", time_to_show=1)
                        except Exception as e:
                            utils.show_status_message(self.__stdscr, str(e), 2)

                    self.__set_email_list()
                    break

                self.__set_email_list(isConfirm=True)
        except:
            utils.show_message(
                self.__stdscr, "Something went wrong! Press 'q' to go back")

    def __display_confirm_bottom_bar_menu(self):
        '''To display confirm email bottom bar'''

        h, _ = self.__stdscr.getmaxyx()

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

    # <!-------------------------------------------------UI Utils---------------------------------------------------->

    def __setup_bottom_bar(self):
        '''To setup bottom bar'''

        BottomBar(self.__stdscr, self.options)


def main(stdscr):
    EMAIL_LIST(stdscr, "INBOX", None)


if __name__ == "__main__":
    curses.wrapper(main)
