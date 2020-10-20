import curses, textwrap, os, time, re, getpass
from curses.textpad import Textbox, rectangle
from BottomBar import BottomBar
from dotenv import load_dotenv
from SMTP.main import SEND_MAIL
from threading import Thread
from Title import Title
import utils

'''Class which handles all the UI part of write mail'''
class Write_Mail_UI:
    
    #<---------------------------------------------Variables--------------------------------------------->
    __stdscr = None
    __email_from = ""
    __email_to = ""
    __key = 0
    __title = "Send a new mail"
    __subject = ""
    __body = ""
    __pass = ""
    # This flag becomes true when mail is sent
    __is_mail_sent = False


    #Confirm Email Variables
    __curr_confirm_index = 0
    # TODO: Later changes this array to title and function dictionary
    __confirm_menu =["YES", "NO"]


    # Default Input messages
    __default_subject_input_msg = "Enter Subject of Mail(Press Ctrl + G to save)"
    __default_body_input_msg = "Enter body of Mail(Press Ctrl + G to save)"


    # Key variables (what happens when which key is pressed)
    # TODO: Change this key which are placed less
    __EDIT_BODY = ord('b')
    __EDIT_SUBJECT = ord('s')
    __QUIT = ord('q')
    __CONFIRM_MAIL = ord('m')
    __EDIT_MAIL_TO_KEY = ord('t')

    




    #<----------------------------------------------Constructor--------------------------------------------->
    # Arguements:
    # Stdscr: Standard screen of curses
    # TODO: Later will need to take email_from from file
    def __init__(self, stdscr):
        # Get the environment filepath
        user = getpass.getuser()
        dir_path = '/home/'+user+'/.termmail'
        env_path = dir_path + "/.env"
        load_dotenv(env_path)
        curses.curs_set(0)
        self.__stdscr = stdscr
        self.__stdscr.border(0)
        self.__email_from = os.getenv('EMAIL')
        self.__pass = os.getenv('PASSWORD')

        self.__setup_color_pairs()
        self.__draw()



    #<--------------------------------------------------Private Functions-------------------------------------------->
    
    '''Main function which draws all the elements on screen'''
    def __draw(self):
        while (self.__key != self.__QUIT) and not self.__is_mail_sent:
            self.__stdscr.clear()
            
            self.__set_default_screen(self.__title, isMain= True)

            self.__set_main_layout()
            
            self.__key = self.__stdscr.getch()

            # TODO: Setup every string according to width and height 
            # TODO: Implement scroll view on small screen
            if self.__key == self.__EDIT_SUBJECT:
                self.__subject = self.__edit_box(self.__default_subject_input_msg, self.__default_subject_input_msg, self.__subject)
            elif self.__key == self.__EDIT_BODY:
                self.__body = self.__edit_box(self.__default_body_input_msg, self.__default_body_input_msg, self.__body, size=2)
            elif self.__key == self.__EDIT_MAIL_TO_KEY:
                self.__email_to = self.__edit_mail_to(self.__email_to).strip()
            elif self.__key == self.__CONFIRM_MAIL:
                self.__set_default_screen(self.__title, isConfirm = True)

            




    #<-------------------------------------------------------------Main layout functions------------------------------------------------>

    
    '''Function which sets up the whole layout of main page'''
    def __set_main_layout(self):
        from_start = 3
        from_block_total = 4
        subject_lines = 4
            
            
        h, w = self.__stdscr.getmaxyx()
        # From, To part of UI
        self.__stdscr.addstr(from_start, 1, "From: " + self.__email_from)
        rectangle(self.__stdscr, from_start - 1, 0, from_start + 1, w - 1)
        self.__stdscr.addstr(from_start + 2, 1, "To: " + self.__email_to)
        rectangle(self.__stdscr, from_start - 1, 0, from_start + 3, w - 1)

        # Subject part of UI
        rectangle(self.__stdscr, from_start + from_block_total, 0, from_start + from_block_total + subject_lines, w - 1)
        self.__stdscr.addstr(from_start + from_block_total, 2, " SUBJECT ")

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
        body_arr = wrapper.wrap(self.__body)
        max_lines = (h - 5) - (from_block_total + from_start + subject_lines + 1)
        for index, body in enumerate(body_arr):
            # ellipsize the text if it can't be fit into the box
            if index == max_lines:
                body = body[0:w-10] + elipsize
                self.__stdscr.addstr(13 + index, 1, body)
                break
            self.__stdscr.addstr(13 + index, 1, body)



    '''Function to show edit text box on screen'''
    # Arguements:
    # input_msg = Message to show on edit text box
    # placeholder = Default value of edit textbox
    # size = Size of edit box (0 = Small, 1 = Medium, 2 = Large, 3 = Extra large)
    def __edit_box(self, title, input_msg, placeholder = "", size = 0):
        curses.curs_set(1)
        self.__set_default_screen(title)
        # self.__stdscr.addstr(0, 0, input_msg)
        _, w = self.__stdscr.getmaxyx()

        # create a new window
        

        number_of_lines = (size + 1) * 5
        number_of_columns = w - 3

        editwin = curses.newwin(number_of_lines, number_of_columns, 2, 1)
        rectangle(self.__stdscr, 1, 0, 2 + number_of_lines, 2 + number_of_columns)
        self.__stdscr.refresh()

        editwin.insstr(placeholder)

        # Make this new window a textbox to edit
        box = Textbox(editwin)
        # box.stripspaces = True
        box.edit()
        

        self.__set_default_screen(self.__title, isMain = True)

        curses.curs_set(0)
        return box.gather()

    
    '''To edit mail to field'''
    # Arguements:
    # to: Mail to default value
    def __edit_mail_to(self, to):
        curses.curs_set(1)
        h, w = self.__stdscr.getmaxyx()
        to_msg = "To (Ctrl + G to save): "
        editwin = curses.newwin(1, w - 5, 5, len(to_msg) + 1)
        editwin.insstr(to)
        self.__stdscr.attron(curses.A_BOLD)
        self.__stdscr.addstr(5, 1, to_msg)
        self.__stdscr.attroff(curses.A_BOLD)
        self.__stdscr.refresh()
        box = Textbox(editwin)
        box.stripspaces = True
        box.edit()

        self.__set_main_layout()
        curses.curs_set(0)
        return box.gather()




    '''Setup Default Screen with title'''
    # Arguements
    # title: Main title of screen
    # isMain: Is the bottom bar is for main screen
    # isConfirm: Is the bottom bar for confirm sending mail screen
    def __set_default_screen(self, title, isMain = False, isConfirm = False):
        self.__stdscr.clear()
            
        Title(self.__stdscr, title)

        # Gives instructions to get different things done
        if isMain:
            self.__set_bottom_bar()
        
        # Need to call set main layout again as second function goes in infinite while loop
        if isConfirm:
            self.__set_main_layout()
            self.__set_confirm_email_bar()

        self.__stdscr.refresh()
        
    
    
    

    

    '''Setup bottom bar'''
    def __set_bottom_bar(self):
        options = [
            {'key': 'S', 'msg': 'Edit Subject of Mail'},
            {'key': 'B', 'msg': 'Edit Body of Mail'},
            {'key': 'M', 'msg': 'Send Mail'},
            {'key': 'Q', 'msg': 'Go Back'},
            {'key': 'T', 'msg': 'Edit Mail To'},
            {'key': 'A', 'msg': 'Add acknowledgement'}
        ]
        # show the bottom bar
        BottomBar(self.__stdscr, options)



    '''To display confirm email bottom bar'''
    # TODO: Later get title and functionality in array (for now only title is present)
    def __display_bottom_bar_menu(self):
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



    '''Setup confirm email bar'''
    def __set_confirm_email_bar(self):
        h, w = self.__stdscr.getmaxyx()
        rectangle(self.__stdscr, h - 4, 0, h - 1, w - 2)
        title = " Confirm sending email ".upper()
        self.__stdscr.attron(curses.A_BOLD)
        self.__stdscr.addstr(h - 4, 1, title)
        self.__stdscr.attroff(curses.A_BOLD)
        self.__display_bottom_bar_menu()

        
        while 1:
            key = self.__stdscr.getch()

            if key == curses.KEY_UP and self.__curr_confirm_index != 0:
                self.__curr_confirm_index -= 1
            elif key == curses.KEY_DOWN and self.__curr_confirm_index != len(self.__confirm_menu) - 1:
                self.__curr_confirm_index += 1

            # TODO: Do the functionality according to choice of user
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.__curr_confirm_index == 0:
                    # Send mail using SMTP class and go back
                    # TODO: Check if subject or body is not empty
                    # Show sending mail status message
                    utils.show_status_message(self.__stdscr, "Sending email....", isLoading=True)
                    try:
                        self.__check_validation()
                        # Authenticate
                        smtp = SEND_MAIL(self.__email_from, self.__pass)
                        # Send mail
                        smtp.send_email(self.__email_to, self.__subject, self.__body)

                        # Show mail sent successfully message
                        utils.show_status_message(self.__stdscr, "Mail sent Successfully", time_to_show=1.5)

                        self.__is_mail_sent = True

                        # Quit from smtp server
                        smtp.quit()
                    except Exception as e:
                        utils.show_status_message(self.__stdscr, str(e), 2)

                self.__set_default_screen(self.__title, isMain= True)
                break

            self.__display_bottom_bar_menu()




    #<--------------------------------------------Utility functions---------------------------------------->

    '''To check if all the data filled is valid'''
    def __check_validation(self):
        # To check if receiver email is empty
        if self.__email_to == "":
            raise Exception("Please Enter Receiver Email")
        # To check if subject is empty
        if self.__subject == "":
            raise Exception("Please Enter Subject Of Email")
        # To check if body is empty
        if self.__body == "":
            raise Exception("Please Enter Body Of Email")
        
    
    '''Function to setup color pairs required'''
    def __setup_color_pairs(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            
        
        

def main(stdscr):
    Write_Mail_UI(stdscr)

if __name__ == "__main__":

    curses.wrapper(main)