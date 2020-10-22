import curses, textwrap, os, time, re, getpass
from curses.textpad import Textbox, rectangle
from BottomBar import BottomBar
from dotenv import load_dotenv
from SMTP.main import SEND_MAIL
from threading import Thread
import utils
from email.base64mime import body_encode as encode_64
import email.mime.multipart
import email.mime.text
import email.mime.application


class Write_Mail_UI:
    '''Class which handles all the UI part of write mail

        Arguements \t
        Stdscr: Standard screen of curses
    '''

    
    #<---------------------------------------------Variables--------------------------------------------->
    __stdscr = None
    __email_from = ""
    __email_to = ""
    __key = 0
    __title = "Send a new mail"
    __subject = ""
    __body = ""
    __pass = ""
    __attachments = ""
    # This flag becomes true when mail is sent
    __is_mail_sent = False


    #Confirm Email Variables
    __curr_confirm_index = 0
    # TODO: Later changes this array to title and function dictionary
    __confirm_menu =["YES", "NO"]


    # Default Input messages
    __default_subject_input_msg = "Enter Subject of Mail (Press Ctrl + G to save)"
    __default_body_input_msg = "Enter body of Mail (Press Ctrl + G to save)"
    __default_attachment_msg = "Enter attachments absolute path"


    # Key variables (what happens when which key is pressed)
    # TODO: Change this key which are placed less
    __EDIT_BODY = ord('b')
    __EDIT_SUBJECT = ord('s')
    __QUIT = ord('q')
    __CONFIRM_MAIL = ord('m')
    __EDIT_MAIL_TO_KEY = ord('t')
    __EDIT_ATTACHMENT = ord('a')

    

    #<----------------------------------------------Constructor--------------------------------------------->
    
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
    
    
    
    def __draw(self):
        '''Main function which shows all the elements on screen'''

        start = 0
        max_lines = self.__set_main_layout(self.__body.splitlines()[start:])
        while (self.__key != self.__QUIT) and not self.__is_mail_sent:
            self.__stdscr.clear()
            

            h, w = self.__stdscr.getmaxyx()
            
            self.__set_default_screen(self.__title, isMain= True)

            max_lines = max(self.__set_main_layout(self.__body.splitlines()[start:]), max_lines)

            flag = False

            if len(self.__body.splitlines()) < max_lines:
                flag = True

            self.__key = self.__stdscr.getch()

            if self.__key == self.__EDIT_SUBJECT:
                self.__subject = self.__edit_box(self.__default_subject_input_msg, self.__default_subject_input_msg, self.__subject)
            elif self.__key == self.__EDIT_BODY:
                self.__body = self.__edit_box(self.__default_body_input_msg, self.__default_body_input_msg, self.__body, size = h - 4)
            elif self.__key == self.__EDIT_ATTACHMENT:
                self.__attachments = self.__edit_box(self.__default_attachment_msg,self.__default_attachment_msg, self.__attachments, is_attachment=True)
            elif self.__key == self.__EDIT_MAIL_TO_KEY:
                self.__email_to = self.__edit_mail_to(self.__email_to).strip()
            elif self.__key == self.__CONFIRM_MAIL:
                self.__set_default_screen(self.__title, isConfirm = True)
            
            # To move body according to up and down lines
            if not flag:
                if self.__key == curses.KEY_DOWN and start <= len(self.__body.splitlines()) - max_lines - 1:
                    start += 1
                elif self.__key == curses.KEY_UP and start > 0:
                    start -= 1
            


    #<-------------------------------------------------------------Main layout functions------------------------------------------------>

    
    
    def __set_main_layout(self, body):
        '''Function which sets up the whole layout of main page'''

        from_start = 3
        from_block_total = 4
        subject_lines = 4
        attachment_block = 0
            
        h, w = self.__stdscr.getmaxyx()
        # From, To part of UI
        # self.__stdscr.addstr(from_start, 1, "From: " + self.__email_from)
        # rectangle(self.__stdscr, from_start - 1, 0, from_start + 1, w - 1)
        rectangle(self.__stdscr, from_start - 1, 0, from_start + 2, w - 1)
        self.__stdscr.addstr(from_start - 1, 2, " To: ")
        self.__stdscr.addstr(from_start, 2, self.__email_to)

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

        
        # If attachment is present show the block for attachment
        if len(self.__attachments.strip()) != 0:
            attachment_block = 2
            attachment_start = from_start + from_block_total + subject_lines

            # Convert attachment array to string
            filename_string = "  ".join(str(index + 1) + "." + name for index, name in enumerate(self.__attachments.split(';')))
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
        return max_lines
        

    
    # Arguements:
    # input_msg = Message to show on edit text box
    # placeholder = Default value of edit textbox
    # size = Size of edit box (default to 5)
    # is_attachment = Is the edit text box if for attachments (Used to hint message)
    def __edit_box(self, title, input_msg, placeholder = "", size = 5, is_attachment = False):
        '''Function to show edit text box on screen'''

        curses.curs_set(1)
        self.__set_default_screen(title)
        # self.__stdscr.addstr(0, 0, input_msg)
        _, w = self.__stdscr.getmaxyx()

        number_of_lines = size
        number_of_columns = w - 3

        # create a new window
        editwin = curses.newwin(number_of_lines, number_of_columns, 2, 1)
        rectangle(self.__stdscr, 1, 0, 2 + number_of_lines, 2 + number_of_columns)
        if is_attachment:
            self.__stdscr.addstr(number_of_lines + 3, 1, "* Use ; to separate multiple filepaths")
        self.__stdscr.refresh()

        editwin.insstr(placeholder)

        # Make this new window a textbox to edit
        box = Textbox(editwin)
        # box.stripspaces = True
        box.edit()
        
        self.__set_default_screen(self.__title, isMain = True)
        curses.curs_set(0)
        return box.gather()

    
    
    # Arguements:
    # to: Mail to default value
    def __edit_mail_to(self, to):
        '''Edit mail to field'''

        curses.curs_set(1)
        h, w = self.__stdscr.getmaxyx()
        to_msg = " To (Ctrl + G to save): (Use ';' to separate multiple emails)"
        editwin = curses.newwin(1, w - 5, 3, 2)
        editwin.insstr(to)
        self.__stdscr.attron(curses.A_BOLD)
        self.__stdscr.addstr(2, 2, to_msg)
        self.__stdscr.attroff(curses.A_BOLD)
        self.__stdscr.refresh()
        box = Textbox(editwin)
        box.stripspaces = True
        box.edit()

        self.__set_main_layout(self.__body.splitlines())
        curses.curs_set(0)
        return box.gather()


    
    # Arguements
    # title: Main title of screen
    # isMain: Is the bottom bar is for main screen
    # isConfirm: Is the bottom bar for confirm sending mail screen
    def __set_default_screen(self, title, isMain = False, isConfirm = False):
        '''Setup Default Screen with title'''

        self.__stdscr.clear()    
        utils.set_title(self.__stdscr, title)

        # Gives instructions to get different things done
        if isMain:
            self.__set_bottom_bar()
        
        # Need to call set main layout again as second function goes in infinite while loop
        if isConfirm:
            self.__set_main_layout(self.__body.splitlines())
            self.__set_confirm_email_bar()

        self.__stdscr.refresh()
    

    def __set_bottom_bar(self):
        '''Setup bottom bar'''

        options = [
            {'key': 'S', 'msg': 'Edit Subject of Mail'},
            {'key': 'B', 'msg': 'Edit Body of Mail'},
            {'key': 'M', 'msg': 'Send Mail'},
            {'key': 'Q', 'msg': 'Go Back'},
            {'key': 'T', 'msg': 'Edit Mail To'},
            {'key': 'A', 'msg': 'Add Attachment'}
        ]
        # show the bottom bar
        BottomBar(self.__stdscr, options)

    
    def __display_bottom_bar_menu(self):
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


    def __set_confirm_email_bar(self):
        '''Setup confirm email bar'''

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
                        receiver_emails = self.__email_to.split(';')
                        data = smtp.add_attachment(self.__subject, self.__body, self.__attachments.split(';'))
                        smtp.send_email(receiver_emails, data=data)

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

   
    def __setup_body(self):
        '''To add attachments in body message'''

        msg = email.mime.multipart.MIMEMultipart()
        body = email.mime.text.MIMEText(self.__body.strip())
        msg.attach(body)
        paths = self.__attachments.split(';')
        for filepath in paths:
            pdf_file = open(filepath.strip(), 'rb')
            attach = email.mime.application.MIMEApplication(pdf_file.read(), _subtype="pdf")
            pdf_file.close()
            attach.add_header("Content-Disposition", "attachment", filename="test.pdf")
            msg.attach(attach)
        return msg.as_string()


    def __check_validation(self):
        '''To check if all the data filled is valid'''
        # To check if receiver email is empty
        if self.__email_to == "":
            raise Exception("Please Enter Receiver Email")
        # To check if subject is empty
        if self.__subject == "":
            raise Exception("Please Enter Subject Of Email")
        # To check if body is empty
        if self.__body == "":
            raise Exception("Please Enter Body Of Email")
        
    
    def __setup_color_pairs(self):
        '''Function to setup color pairs required'''
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            
        
        

def main(stdscr):
    Write_Mail_UI(stdscr)

if __name__ == "__main__":

    curses.wrapper(main)