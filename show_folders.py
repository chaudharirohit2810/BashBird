from IMAP.main import IMAP
from loading import Loading
from menu import Menu
from dotenv import load_dotenv
import os
import curses

class Show_Folders:
    __stdscr = None

    def __init__(self, stdscr):
        self.__stdscr = stdscr
        loading = Loading(stdscr)
        loading.start()
        load_dotenv()
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')
        imap = IMAP(email, password)
        folders = imap.get_mailboxes()
        if folders['success']:
            folders = folders['folders']
            print(folders)
            options = []
            for item in folders:
                options.append({'title': item[1:-1]})
            options.append({'title': "Back", 'Function': None})
            loading.stop()
            Menu(self.__stdscr, options, "Folders")
        else:
            loading.stop()


# if __name__ == "__main__":
#     curses.wrapper(main)    
