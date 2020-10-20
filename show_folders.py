from IMAP.main import IMAP
from loading import Loading
from menu import Menu
from dotenv import load_dotenv
import os, curses, getpass
from email_list import EMAIL_LIST

class Show_Folders:
    __stdscr = None

    def __init__(self, stdscr):
        self.__stdscr = stdscr
        loading = Loading(stdscr)
        loading.start()
        # Get the environment filepath
        user = getpass.getuser()
        dir_path = '/home/'+user+'/.termmail'
        env_path = dir_path + "/.env"
        load_dotenv(env_path)
        
        
        try:
            email = os.getenv('EMAIL')
            password = os.getenv('PASSWORD')
            imap = IMAP(email, password)
            folders = imap.get_mailboxes()
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
