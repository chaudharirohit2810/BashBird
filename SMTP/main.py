from socket import *
import ssl
from dotenv import load_dotenv
import os
from email.base64mime import body_encode as encode_64
import email.mime.multipart
import email.mime.text
import email.mime.image
import email.mime.application
import mimetypes
import base64


# Public Functions     Functionality
# ---------------------------------------------------------------------------------------------------------------
# Constructor          Logins to smtp server using provided email and password
# send_email           Sends mail to mail server

class SMTP:
    '''Class which does all the part of IMAP Protocol

    Arguements: \t
    email: User email \t
    password: User password\t
    smtp_server: Url of smtp server (default: gmail)\t
    debugging: Utility variable to print sent and received messages
    '''

    # <--------------------------------------------Variables----------------------------------------->

    # Stores socket which connects to mail server
    main_socket = None

    # SMTP Protocol messages to connect to smtp server
    __DEFAULT_HELLO_MSG = "EHLO Rohit"
    __AUTH_MSG = "AUTH LOGIN"
    __MAIL_FROM = "MAIL FROM: "
    __RCPT_TO = "RCPT TO: "
    __DATA = "DATA"
    __STARTTLS = "STARTTLS"
    __MAIL_NEW_LINE = "\r\n"
    __QUIT = "QUIT"
    __END_MSG = "\r\n.\r\n"

    # Default timeout for socket
    __TIMEOUT = 15  # 15 seconds for now

    # Port and host to connect to smtp server
    __SSL_PORT = 465
    __HOST = ''

    # Stores the smtp server address and port for each domain
    __HOST_EMAIL_PAIR = [
        {
            'domain': 'gmail.com',
            'smtp_server': 'smtp.gmail.com',
            'port': 465,
            'is_tls': False
        },
        {
            'domain': 'coep.ac.in',
            'smtp_server': 'outlook.office365.com',
            'port': 587,
            'is_tls': True
        },
        {
            'domain': 'outlook.com',
            'smtp_server': 'outlook.office365.com',
            'port': 993,
            'is_tls': True
        }
    ]

    # To start the tls if smtp server requires starttls encryption (for outlook)
    __is_tls = False

    # Utility variable to print debugging output
    __debugging = False

    # email and password
    __email = ""
    __password = ""

    # <-------------------------------------------Functions----------------------------------------------->

    def __init__(self, email, password, debug=False):
        self.__email = email
        self.__password = password
        self.__debugging = debug
        email_domain = email.split('@')[1].lower()

        for email in self.__HOST_EMAIL_PAIR:
            if email['domain'] == email_domain:
                self.__HOST = email['smtp_server']
                self.__SSL_PORT = email['port']
                self.__is_tls = email['is_tls']
                break

        # Connect to smtp server
        self.__connect()

        # Say "EHLO" to server
        self.__say_hello()

        # Login using email and password
        self.__login()

    # <--------------------------------------------Public functions---------------------------------------------->

    def send_email(self, mail_to, data):
        '''Function which is used to send mail

         Arguements \t
         mail_to : The email address of receiver \t
         data: Body of mail \t

        '''
        # print('Sending mail..................')
        self.__send_main_from()
        for item in mail_to:
            self.__send__RCPT_TO(item.strip())
        self.__send__DATA(data)

    def add_attachment(self, subject, text, filepaths):
        '''To add attachments, subject and text together to make body

            Arguements \t
            subject: Subject of email \t
            text: Text body \t
            filepaths: Filepaths of attachments

        '''
        try:
            msg = email.mime.multipart.MIMEMultipart()
            msg['Subject'] = subject
            body = email.mime.text.MIMEText(text)
            msg.attach(body)
            for filepath in filepaths:
                filepath = filepath.strip()
                if filepath != None and len(filepath) != 0:
                    attach = None
                    file_type = mimetypes.MimeTypes().guess_type(filepath)[0]
                    # Check if mimetype starts from application
                    if file_type.startswith('application/'):
                        application_file = open(filepath, 'rb')
                        attach = email.mime.application.MIMEApplication(
                            application_file.read(), _subtype=file_type.split('/')[1])
                        application_file.close()
                    # Check if attachment is image
                    elif file_type.startswith('image/'):
                        image_file = open(filepath, 'rb')
                        attach = email.mime.image.MIMEImage(
                            image_file.read(), _subtype=file_type.split('/')[1])
                        image_file.close()
                    attach.add_header(
                        "Content-Disposition", "attachment", filename=os.path.basename(filepath))
                    msg.attach(attach)
            return msg.as_string()
        except:
            raise Exception("Invalid filename")

    def quit(self):
        '''Send QUIT to server when conversation is complete'''

        self.__send_encoded_msg(self.__QUIT)

    # <-------------------------------------Private functions----------------------------------------------->

    # <------------------------T----------To connect to smtp server------------------------------------------>

    def __connect(self):
        '''Function which connects to smtp server'''

        # Start TCP connection with smtp server
        self.main_socket = socket(AF_INET, SOCK_STREAM)
        self.main_socket.settimeout(self.__TIMEOUT)
        self.main_socket.connect((self.__HOST, self.__SSL_PORT))
        msg = ""

        # If the smtp server requires starttls encryption (for outlook)
        if self.__is_tls:
            msg = self.main_socket.recv(1024).decode().strip('\r\t\n')
            self.__say_hello()
            self.__start_tls()
            self.__ssl_connect()
        else:
            self.__ssl_connect()
            msg = self.main_socket.recv(1024).decode().strip('\r\t\n')

        code = int(msg[:3])
        if self.__debugging:
            print(msg)

        if code != 220:
            raise Exception("Connection Failed")

    def __say_hello(self):
        '''Saying hello to server to establish connection between client and server'''

        if self.__debugging:
            print('Saying hello to server')

        self.__send_encoded_msg(self.__DEFAULT_HELLO_MSG)

    def __start_tls(self):
        '''Starting the TLS encryption'''
        self.__send_encoded_msg(self.__STARTTLS)

    def __ssl_connect(self):
        '''Function to connect to smtp server with ssl'''

        context = ssl.create_default_context()
        host = self.__HOST

        self.main_socket = context.wrap_socket(
            self.main_socket, server_hostname=host)

    def __close__connection(self):
        '''Function to close the connection with smtp server'''

        self.main_socket.close()

    # <---------------------------------------------------AUTH----------------------------------------------------->

    def __login(self):
        '''Function which does the authentication part'''

        # Tell smtp server for authentication
        code, reply = self.__send_encoded_msg(self.__AUTH_MSG)

        # Send email
        encoded_mail = encode_64(self.__email.encode('ascii'), eol='')
        code, reply = self.__send_encoded_msg(encoded_mail)

        # Send password of mail
        encoded_pass = encode_64(self.__password.encode('ascii'), eol='')
        pass_msg = encoded_pass
        code, reply = self.__send_encoded_msg(pass_msg)
        if code == 235:
            pass
        else:
            raise Exception('Invalid username or password')

    # <-----------------------------------------Send mail-------------------------------------------------->

    def __send_main_from(self):
        '''Send "mail from" to smtp server'''

        msg = self.__MAIL_FROM + "<" + self.__email + "> "
        code, reply = self.__send_encoded_msg(msg)
        # If reponse code is not 250 then sender mail is not valid
        if code != 250:
            raise Exception('Invalid sender mail')

    def __send__RCPT_TO(self, mail_to):
        '''Send whom to send mail to smtp server'''

        msg = self.__RCPT_TO + "<" + mail_to + ">"
        code, reply = self.__send_encoded_msg(msg)
        # If code is not 250 then receiver mail is not valid
        if code != 250:
            raise Exception('Invalid receiver mail')

    def __send__DATA(self, data):
        '''Send subject and body of mail to server'''

        # Send "DATA" to smtp server
        code, reply = self.__send_encoded_msg(self.__DATA)
        # If code is not 354 then something is wrong with smtp server
        if code != 354:
            raise Exception('Something went wrong')

        self.main_socket.send(data.encode())

        # Send end message to tell smtp server that mail has ended
        code, reply = self.__send_encoded_msg(self.__END_MSG)

        # If response code is not 250 then mail raise exception mail not sent successfully
        if code != 250:
            raise Exception('Mail not sent successfully! Please try again')

    # <-----------------------------------------------Utils----------------------------------------------------->
    ''' Utility function to send encoded message to smtp server'''

    def __send_encoded_msg(self, message):
        if self.__debugging:
            print("Client: ", message)
        message = message + self.__MAIL_NEW_LINE
        self.main_socket.send(message.encode('ascii'))
        received_msg = self.main_socket.recv(1024).decode().strip('\r\t\n')
        if self.__debugging:
            print(received_msg)
        return int(received_msg[:3]), received_msg[4:]


if __name__ == "__main__":
    load_dotenv(dotenv_path='./.env')
    old_mail = os.getenv('EMAIL')
    old_pass = os.getenv('PASSWORD')
    SMTP(old_mail, old_pass, debug=True)
