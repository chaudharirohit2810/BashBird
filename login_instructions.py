from curses.textpad import rectangle
import textwrap
import curses
import utils
from BottomBar import BottomBar


class Instructions:
    '''Class which shows login instructions

        Arguements \t
        stdscr: Standard screen of curses 

    '''

    # <!----------------------------------------------Variables----------------------------------------------------->
    # Standard screen of curses
    __stdscr = None

    __app_password = ["1. Go to your Google Account",
                      "2. Select Security",
                      '3. Under "Signing in to Google", select App passwords. You may need to sign in.',
                      '4. At the bottom, choose Select app and choose the app you using and then Select device and choose the device you’re using and then Generate.',
                      '5. Follow the instructions to enter the App Password. The App Password is the 16-character code in the yellow bar on your device.',
                      '6. Tap Done',
                      "7. Login to app using your email and generated app password"
                      ]

    __less_secure = ["1. Go to your Google Account",
                     "2. Select Security. ",
                     "3. Click Turn on access link under Less secure app access section in right.",
                     "4. Now turn on Allow less secure apps:ON toggle button in the new page.",
                     "5. Now login to app using your email and password"
                     ]

    options = [
        {'key': 'Q', 'msg': 'Go Back'}
    ]

    __screen_size_msg = "Screen size is too small! Please increase screen size"

    # <!----------------------------------------------Functions----------------------------------------------------->

    def __init__(self, stdscr):
        self.__stdscr = stdscr
        self.__set_main_layout()

    def __set_main_layout(self):
        '''Main function which setups the layout'''

        key = 0

        while key != ord('q'):
            h, w = self.__stdscr.getmaxyx()

            try:

                wrapper = textwrap.TextWrapper(width=w - 3)
                self.__stdscr.clear()
                utils.set_title(self.__stdscr, "LOGIN INSTRUCTIONS")
                start = self.__setup_array_text(
                    wrapper, w, 2, self.__app_password, " Login Using App Password (Recommended):  ")
                start = self.__setup_array_text(
                    wrapper, w, start + 2, self.__less_secure, " Enable less Secure apps :  ")
                # show the bottom bar
                BottomBar(self.__stdscr, self.options)
                self.__stdscr.refresh()
                key = self.__stdscr.getch()
            except:
                self.__stdscr.clear()
                wrapper = textwrap.TextWrapper(width=w-2)
                error_msgs = wrapper.wrap(self.__screen_size_msg)
                for index, msg in enumerate(error_msgs):
                    x_pos = w // 2 - len(msg) // 2
                    y_pos = h // 2 + index
                    self.__stdscr.addstr(y_pos, x_pos, msg)
                self.__stdscr.refresh()

    # Arguements:
    # wrapper: Textwrap wrapper to wrap the text
    # width: Width of the screen
    # st: Start of text
    # text: Text to show
    # title: Title of text

    def __setup_array_text(self, wrapper, width, st, text, title):
        '''To set up the text '''

        old_start = st
        start = old_start + 1
        start += 1
        for item in text:
            item_arr = wrapper.wrap(item)
            for subitem in item_arr:
                self.__stdscr.addstr(start, 2, subitem)
                start += 1
        rectangle(self.__stdscr, old_start, 0, start, width - 2)
        self.__stdscr.attron(curses.A_BOLD)
        self.__stdscr.addstr(
            old_start, 1, title)
        self.__stdscr.attroff(curses.A_BOLD)
        return start
