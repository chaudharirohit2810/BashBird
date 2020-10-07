import curses, textwrap, os
from curses.textpad import Textbox, rectangle
from BottomBar import BottomBar
from dotenv import load_dotenv

'''Class which handles all the UI part of write mail'''
class Write_Mail_UI:
    
    #<---------------------------------------------Variables--------------------------------------------->
    __stdscr = None
    __email_from = "chaudharirohit2810@gmail.com"
    __email_to = "rohitkc2810@gmail.com"
    __key = 0
    __title = "Send a new mail"
    __subject = ""
    __body = ""


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

    




    #<----------------------------------------------Constructor--------------------------------------------->
    # Arguements:
    # Stdscr: Standard screen of curses
    # TODO: Later will need to take email_from from file
    def __init__(self, stdscr):
        load_dotenv()
        self.__stdscr = stdscr
        self.__stdscr.border(0)
        email = os.getenv('EMAIL')
        self.__email_from = email
        self.__setup_color_pairs()
        self.__draw()



    #<--------------------------------------------------Private Functions-------------------------------------------->
    
    '''Main function which draws all the elements on screen'''
    def __draw(self):
        while (self.__key != self.__QUIT):
            self.__stdscr.clear()
            
            self.__set_default_screen(self.__title, isMain= True)

            # TODO: Setup every string according to width and height 
            # TODO: Implement scroll view on small screen
            if self.__key == self.__EDIT_SUBJECT:
                self.__subject = self.__edit_box(self.__default_subject_input_msg, self.__default_subject_input_msg, self.__subject)
            elif self.__key == self.__EDIT_BODY:
                self.__body = self.__edit_box(self.__default_body_input_msg, self.__default_body_input_msg, self.__body, size=2)
            elif self.__key == self.__CONFIRM_MAIL:
                self.__set_default_screen(self.__title, isConfirm = True)

            self.__set_main_layout()
            
            self.__key = self.__stdscr.getch()




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
        max_lines = (h - 5) - (from_block_total + from_start + subject_lines + 1) - 2
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
        box.stripspaces = True
        box.edit()
        

        self.__set_default_screen(self.__title, isMain = True)

        curses.curs_set(0)
        return box.gather()




    '''Setup Default Screen with title'''
    # Arguements
    # title: Main title of screen
    # isMain: Is the bottom bar is for main screen
    # isConfirm: Is the bottom bar for confirm sending mail screen
    def __set_default_screen(self, title, isMain = False, isConfirm = False):
        self.__stdscr.clear()
            
        self.__set_title(title)

        # Gives instructions to get different things done
        if isMain:
            self.__set_bottom_bar()
        
        # Need to call set main layout again as second function goes in infinite while loop
        if isConfirm:
            self.__set_main_layout()
            self.__set_confirm_email_bar()

        self.__stdscr.refresh()
        
    
    
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
        self.__stdscr.attron(curses.color_pair(1))
        self.__stdscr.attron(curses.A_BOLD)
        self.__stdscr.addstr(0, 0, temp_title)
        self.__stdscr.attroff(curses.A_BOLD)
        self.__stdscr.attroff(curses.color_pair(1))

    

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
                self.__set_default_screen(self.__title, isMain= True)
                break

            self.__display_bottom_bar_menu()




    #<--------------------------------------------Utility functions---------------------------------------->
    
    '''Function to setup color pairs required'''
    def __setup_color_pairs(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            
        
        

def main(stdscr):
    Write_Mail_UI(stdscr)

if __name__ == "__main__":

    curses.wrapper(main)