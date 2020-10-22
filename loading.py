import curses, time
from threading import *



#  Public Functions     Functionality
#------------------------------------------------------------------------------------------------------------
# Constructor           Required Arguements: stdscr(Standard screen of curses)
# start                 To start the loading
# stop                  To stop the loading

class Loading:
    '''Class which implements loading on screen

    Arguements \t
    stdscr: Standard screen attribute of curses

    '''
    
    #<!---------------------------------------------------Variables------------------------------------------->
    __stdscr = None
    __text = "LOADING"
    __thread = None
    __is_loading = False
    __count = 10



    #<!----------------------------------------------Functions--------------------------------------------------->
    def __init__(self, stdscr):
        self.__stdscr = stdscr


    def __load(self):
        '''To show the loading text on terminal'''

        curses.curs_set(0)
        self.__stdscr.clear()
        temp_count = 1
        while self.__is_loading:
            self.__stdscr.clear()
            text = self.__text
            for _ in range(temp_count):
                text += "."
            h, w = self.__stdscr.getmaxyx()
            x_pos = w // 2 - len(self.__text) // 2
            y_pos = h // 2
            self.__stdscr.attron(curses.A_BOLD)

            self.__stdscr.addstr(y_pos, x_pos, str(text))
            self.__stdscr.attroff(curses.A_BOLD)
            temp_count = temp_count % self.__count + 1
            time.sleep(0.1)
            self.__stdscr.refresh()
        
    
    def start(self):
        '''To start loading'''
        
        self.__is_loading = True
        # create the thread to show loading
        self.__thread = Thread(target=self.__load)
        # Start the thread
        self.__thread.start()

    
    def stop(self):
        '''To stop loading'''

        # making the loading false which stops the while loop in thread
        self.__is_loading = False



def main(stdscr):
    loading = Loading(stdscr)
    loading.start()
    time.sleep(2)
    loading.stop()

if __name__ == "__main__":
    curses.wrapper(main)