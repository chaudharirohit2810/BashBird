from IMAP.main import IMAP
from loading import Loading
from menu import Menu
from dotenv import load_dotenv
import os
import curses
from email_list import EMAIL_LIST

class Show_Folders:
    __stdscr = None

    def __init__(self, stdscr):
        self.__stdscr = stdscr
        loading = Loading(stdscr)
        loading.start()
        load_dotenv('./.env')
        
        
        try:
            email = os.getenv('EMAIL')
            password = os.getenv('PASSWORD')
            imap = IMAP(email, password)
            folders = imap.get_mailboxes()
            folders = folders['folders']
            print(folders)
            options = []
            for item in folders:
                options.append({'title': item[1:-1], 'Function': EMAIL_LIST, 'args': (item, imap)})
            options.append({'title': "Back", 'Function': None, 'args': None})
            loading.stop()
            Menu(self.__stdscr, options, "Folders")

        except:
            loading.stop()


# if __name__ == "__main__":
#     curses.wrapper(main)    
