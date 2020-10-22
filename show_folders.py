from IMAP.main import IMAP
from loading import Loading
from menu import Menu
from dotenv import load_dotenv
import os, curses, getpass
from email_list import EMAIL_LIST
import utils

class Show_Folders:
    '''Show mailboxes on imap server

        Arguements \t
        stdscr: Standard screen of imap server

    '''

    #<!------------------------------------------------Variables----------------------------------------------------->
    __stdscr = None


    #<!----------------------------------------------Functions------------------------------------------------------>
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
            utils.show_message(self.__stdscr, "Something went wrong! Press 'q' to go back")


