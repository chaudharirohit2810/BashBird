from socket import *
import ssl
from dotenv import load_dotenv
import os
from email.base64mime import body_encode as encode_64
import email as email_lib


class IMAP:
    
    #<------------------------------------------------------Variables------------------------------------------>
    # Main socket which does all the work
    __main_socket = None


    __email = ""
    __password = ""

    # Default Messages

    __AUTH_MSG = "a01 LOGIN" # Authentication message
    __MAIL_NEW_LINE = "\r\n"

    # TODO: Use different ports for different hosts
    __SSL_PORT = 993 # Port for gmail imap server
    __HOST = ''
    __TIMEOUT = 15 # 15 seconds for now

    # Dictionary keys
    __success = 'success'
    __msg = 'msg'

    __debugging = False

    


    #<-----------------------------------------------------Constructor------------------------------------------>
    '''Constructor of class'''
    # TODO: Tell user to use less secure setting or to create app password
    # Arguements:
    # Email: Email of user
    # Password: Password of user
    # imap_server: Imap server of his account
    # debugging: Just to util to print (Later needs to be disabled)
    def __init__(self, email, password, imap_server = "imap.gmail.com", debugging = False):
        self.__email = email
        self.__password = password
        self.__HOST = imap_server
        self.__debugging = debugging

        try:
            # Connect to imap server
            self.__connect()
        except Exception as e:
            # TODO: Later will need this to return to UI so remove this line
            print(e)

    
    #<----------------------------------------------Private functions------------------------------------------->

    #<!-------------------------------------------Connection--------------------------------------------------->


    '''Connect to IMAP Server'''
    # Alert: SSL works but check how it works
    def __connect(self):
        # Create a socket
        self.__main_socket = socket(AF_INET, SOCK_STREAM)
        
        # Set timeout for it
        self.__main_socket.settimeout(self.__TIMEOUT)

        # Connect to imap server
        self.__main_socket.connect((self.__HOST, self.__SSL_PORT))

        # Wrap the socket in ssl
        self.__ssl_connect()

        # Receive the message from server
        msg = self.__main_socket.recv(1024).decode().strip('\r\n\t')
        if self.__debugging:
            print("Server:", msg)
        if msg[2:4] != "OK":
            raise Exception("Something Went Wrong! Failed to connect to imap server")
        
        # Login after connection
        self.__login()



    '''To wrap socket in SSL'''
    # Alert: Don't know how it works for now
    def __ssl_connect(self):
        self.__main_socket = ssl.wrap_socket(self.__main_socket)
        
    



    # <!--------------------------------------------Authentication-------------------------------------------->


    '''To login to imap server'''
    def __login(self):
        # Tell imap server for authentication
        message = self.__AUTH_MSG + " " + self.__email + " " + self.__password + self.__MAIL_NEW_LINE
        self.__main_socket.send(message.encode('ascii'))
        recv_msg = self.__main_socket.recv(1024).decode().strip('\r\t\n')
        
        # Split the lines in received message
        lines_arr = recv_msg.splitlines()

        # Get the last line from received lines and split it
        imap_msg_tokens = lines_arr[-1].split(" ")

        # Check if second element of tokens is OK if not raise exception
        if imap_msg_tokens[1] != "OK":
            raise Exception("Invalid username or password")




    # <!-------------------------------------Commands related to IMAP----------------------------------------->

    '''To get all the available mail boxes'''
    # TODO: Later add main mailbox name as arguement which will give sub mailboxes
    def get_mailboxes(self):
        # LIST command which needs to be sent to imap server
        send = 'a02 LIST "" "*"'
        
        code, msg = self.__send_encoded_msg(send)

        if code != "OK":
            return {self.__success: False, 'folders': []}

        # Separate lines of message
        folders_imap = msg.splitlines()
        folders_imap.pop(-1)
        folders = []
        for item in folders_imap:
            # Remove the starting message of imap server which contains "LIST"
            tokens = item.split(" ")
            index = tokens.index('"/"')
            name = ""
            for i in range(index + 1, len(tokens)):
                name += tokens[i]
            if name != '"[Gmail]"':
                folders.append(name)

        # TODO: Check the response correctly

        # Return list of folders except last attribute
        return {self.__success: True, 'folders': folders}

    
    '''To select particular main box'''
    def select_mailbox(self, name):
        send = 'a02 SELECT "{folder_name}"'.format(folder_name = name)
        code, msg = self.__send_encoded_msg(send)
        
        if code != "OK":
            return {self.__success: False, 'msg': "Invalid mailbox name", 'number_of_mails': -1}
        else:
            number_of_mails = 0
            # To get the number of mails in mailbox
            lines_arr = msg.splitlines()
            for item in lines_arr:
                try:
                    tokens = item.split(" ")
                    if tokens[2] == "EXISTS":
                        number_of_mails = int(tokens[1])
                except Exception as e:
                    continue

            return {self.__success: True, 'msg': "Mailbox Selected", 'number_of_mails': number_of_mails}

    
    '''To fetch email'''
    # TODO: Later implement for multiple emails
    # Alert: For now only works for one email
    def fetch_email(self, start, count = 0):
        send = "a02 FETCH " + str(start) + " (RFC822)" + self.__MAIL_NEW_LINE
        self.__main_socket.send(send.encode())
        success, msg = self.__get_whole_message()
        
        if success:
            recv_email = self.__decode_email(msg)
            self.__get_info(recv_email)
        else:
            return {self.__success: False, 'msg': "Failed to fetch email! Please try again"}
        
    



        



    # <-----------------------------------------------Utils----------------------------------------------------->


    ''' Utility function to send encoded message to imap server'''
    def __send_encoded_msg(self, message):
        if self.__debugging:
            print("Client: ", message)
        message = message + self.__MAIL_NEW_LINE
        self.__main_socket.send(message.encode())
        received_msg = self.__main_socket.recv(100024).decode().strip('\r\t\n')
        lines_arr = received_msg.splitlines()
        code = lines_arr[-1].split(" ")[1]
        if self.__debugging:
            print("Server: ", received_msg)
        return code, received_msg

    
    '''To get whole email back from the server'''
    def __get_whole_message(self):
        msg = ""
        email_results = ["OK", "NO", "BAD"]
        while 1:
            try:
                # Receive message from server
                temp_msg = self.__main_socket.recv(1024).decode("utf-8", errors='ignore')
                # print(temp_msg)
                # Split the lines from the received message
                lines_arr = temp_msg.splitlines()
                
                # Check if the last line contains the codes involved in imap protocol
                code = None
                try:
                    code = lines_arr[-1].split(" ")[1]
                except:
                    continue
                if code in email_results:
                    lines_arr.pop(-1)

                    # Add other lines from array to message
                    for item in lines_arr:
                        msg += item
                        msg += self.__MAIL_NEW_LINE

                    return True, msg
                
                msg += temp_msg
            except Exception as e:
                if self.__debugging:
                    print(e)
                return False, "Request Failed"

    


    '''To decode mail from message received from the imap server'''
    # Arguements: 
    # msg   Message received from server
    # Returns the email object by decoding the message
    def __decode_email(self, msg):
        msglines = msg.splitlines()
        main_msg = ""
        for item in msglines:
            # If there is paranthesis on new line then it indicates end of mail according to imap protocol
            if item == ")":
                break
            main_msg += item
            main_msg += "\r\n"
        # Get the message from 'Delivered-To' 
        # header of email starts from here
        main_msg = main_msg[main_msg.find('Delivered-To'):]

        # Use email_lib to separate keys and values 
        raw = email_lib.message_from_string(main_msg)
        
        return raw
    
    '''To get body of mail'''
    # Arguements: 
    # email_obj     The email object
    # Returns the body of email
    def __get_body(self, email_obj):
        if email_obj.is_multipart():
            return self.__get_body(email_obj.get_payload(0))
        else:
            return email_obj.get_payload(None, True).decode()



    '''To get different headers of email'''
    # Arguements
    # email_obj     The email object
    # TODO: Later use it to return the email with required information (Not known right now)
    # Alert: For now it is just printing data Later needs to return data
    def __get_info(self, email_obj):
        # keys = email_obj.keys()
        # for key in keys:
        #     print(key, email_obj[key], sep=": ")
        # return
        # To get To
        print("To:", email_obj['Delivered-To'])

        # To get From
        print("From:", email_obj['From'])

        # To get subject
        print("Subject:", email_obj['Subject'])

        # To get Date
        print("Date:", email_obj['Date'])

        # # To get body of email
        # print("Body: ")
        # print(self.__get_body(email_obj).strip('\r\n'))



if __name__ == "__main__":
    load_dotenv()
    old_mail = os.getenv('EMAIL')
    old_pass = os.getenv('PASSWORD')
    imap = IMAP(old_mail, old_pass, debugging=True)
    folders = imap.get_mailboxes()
    # print(folders)
    out = imap.select_mailbox('INBOX')
    num = out['number_of_mails']
    mail_list = []
    for i in range(1, 20):
        imap.fetch_email(num - i)
        print()