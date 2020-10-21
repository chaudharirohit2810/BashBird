from socket import *
import ssl
from dotenv import load_dotenv
import os
from email.base64mime import body_encode as encode_64
import email.mime.multipart
import email.mime.text, email.mime.image, email.mime.application
import mimetypes


'''Class which does all the part of SMTP Protocol'''
# Public Functions     Functionality
#---------------------------------------------------------------------------------------------------------------
# Constructor          Logins to smtp server using provided email and password
# send_email           Sends mail to mail server

class SEND_MAIL:


    #<--------------------------------------------Variables----------------------------------------->

    # Stores socket which connects to mail server
    main_socket = None

    # SMTP Protocol messages to connect to smtp server
    __DEFAULT_HELLO_MSG = "EHLO Rohita"
    __AUTH_MSG = "AUTH LOGIN"
    __MAIL_FROM = "MAIL FROM: "
    __RCPT_TO = "RCPT TO: "
    __DATA = "DATA"
    __MAIL_NEW_LINE = "\r\n"
    __QUIT = "QUIT"
    __END_MSG = "\r\n.\r\n"

    # Default timeout for socket
    __TIMEOUT = 15 # 15 seconds for now

    # Port and host to connect to smtp server
    # TODO: Make a dictionary which stores port and hostname of mail servers like google and outlook
    __PORT = 587 
    __SSL_PORT = 465
    __HOST = ''

    # Utility variable to decide 
    __debugging = False # whether to print debugging output

    # email and password
    __email = ""
    __password = ""



    #<-------------------------------------------Functions----------------------------------------------->

    '''Constructor of SMTP'''
    # Arguements:
    # Email: Email of user
    # Password: Password of user
    # smtp_server : Smtp hostname of server. Default: smtp.gmail.com
    # Debug: Whethere to debug the output (Just for testing)
    def __init__(self, email, password, smtp_server = "smtp.gmail.com", ssl_port=465, debug = False):
            self.__email = email 
            self.__password = password
            self.__HOST = smtp_server
            self.__debugging = debug
            self.__SSL_PORT=ssl_port

            # Connect to smtp server
            self.__connect()

            # Say "EHLO" to server
            self.__say_hello()

            # Login using email and password
            self.__login()




    # <--------------------------------------------Public functions---------------------------------------------->

    # TODO: Also add attachments and CC
    '''Function which is used to send mail'''
    # Arguements:
    # mail_to : The email address of receiver
    # data: Body of mail
    def send_email(self, mail_to, data):
        # print('Sending mail..................')
        self.__send_main_from()
        for item in mail_to:
            self.__send__RCPT_TO(item.strip())   
        self.__send__DATA(data)


    def add_attachment(self, subject, text, filepaths):
        try:
            msg = email.mime.multipart.MIMEMultipart()
            msg['Subject'] = subject
            body = email.mime.text.MIMEText(text)
            msg.attach(body)
            for filepath in filepaths:
                filepath = filepath.strip()
                if filepath != None and len(filepath) != 0:
                    file_type = mimetypes.MimeTypes().guess_type(filepath)[0]
                    # Check if mimetype starts from application
                    if file_type.startswith('application/'):
                        pdf_file = open(filepath, 'rb')
                        attach = email.mime.application.MIMEApplication(pdf_file.read(), _subtype=file_type.split('/')[1])
                        pdf_file.close()
                    # Check if attachment is image
                    elif file_type.startswith('image/'):
                        image_file = open(filepath, 'rb')
                        attach = email.mime.image.MIMEImage(image_file.read(), _subtype=file_type.split('/')[1])
                        image_file.close()
                    attach.add_header("Content-Disposition", "attachment", filename=os.path.basename(filepath))
                    msg.attach(attach)
            return msg.as_string()
        except:
            raise Exception("Invalid filename")


    # TODO: Call this function in destructor
    '''Send QUIT to server when conversation is complete'''
    def quit(self):
        self.__send_encoded_msg(self.__QUIT)

    
    




    
    # <-------------------------------------Private functions-----------------------------------------------> 


    # <------------------------T----------To connect to smtp server------------------------------------------>
    
    '''Function which connects to smtp server'''
    def __connect(self):
            # Start TCP connection with smtp server
            self.main_socket = socket(AF_INET, SOCK_STREAM)
            self.main_socket.settimeout(self.__TIMEOUT)
            self.main_socket.connect((self.__HOST, self.__SSL_PORT))
            self.__ssl_connect()
            msg = self.main_socket.recv(1024).decode().strip('\r\t\n')
            code = int(msg[:3])
            if self.__debugging:
                print(msg)
            
            if code != 220:
                raise Exception("Connection Failed")


    '''Saying hello to server to establish connection between client and server'''
    def __say_hello(self):
        if self.__debugging:
            print('Saying hello to server')
        message = self.__DEFAULT_HELLO_MSG
        self.__send_encoded_msg(self.__DEFAULT_HELLO_MSG)

    
    # Alert: Not sure right now whether it really does ssl (Will need to check)
    '''Function to connect to smtp server with ssl'''
    def __ssl_connect(self):
        context = ssl.create_default_context()
        host = self.__HOST
    
        self.main_socket = context.wrap_socket(self.main_socket, server_hostname=host)



    # TODO : Call this in destructor
    '''Function to close the connection with smtp server'''
    def __close__connection(self):
        self.main_socket.close()



    #<---------------------------------------------------AUTH----------------------------------------------------->

    '''Function which does the authentication part'''
    def __login(self):
        # Tell smtp server for authentication
        code, reply = self.__send_encoded_msg(self.__AUTH_MSG)
        

        # Send email
        encoded_mail = encode_64(self.__email.encode('ascii'), eol = '')
        code, reply = self.__send_encoded_msg(encoded_mail)
        
        
        # Send password of mail
        encoded_pass = encode_64(self.__password.encode('ascii'), eol = '')
        pass_msg = encoded_pass
        code, reply = self.__send_encoded_msg(pass_msg)
        if code == 235:
            # print('You are logged in')
            pass
        else: 
            raise Exception('Invalid username or password')





    
    # <-----------------------------------------Send mail-------------------------------------------------->

    '''Send "mail from" to smtp server'''
    def __send_main_from(self):
        msg = self.__MAIL_FROM + "<" + self.__email + "> "
        code, reply = self.__send_encoded_msg(msg)
        # If reponse code is not 250 then sender mail is not valid
        if code != 250:
            raise Exception('Invalid sender mail')


    '''Send whom to send mail to smtp server'''
    # mail_to : email address of receiver
    def __send__RCPT_TO(self, mail_to):
        msg = self.__RCPT_TO + "<" + mail_to + ">"
        code, reply = self.__send_encoded_msg(msg)
        # If code is not 250 then receiver mail is not valid
        if code != 250:
            raise Exception('Invalid receiver mail')


    '''Send subject and body of mail to server'''
    # data: body of mail
    def __send__DATA(self, data):
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
        
        # print('Mail sent successfully')

   




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
    # ins = SEND_MAIL(old_mail, old_pass, debug = True)
    # email_send = "rohitkc2810@gmail.com"
    # subject = input('Enter the subject: ')
    # subject = "This is to check attachment part"
    # body = "He kaskai chalat mag"
    # body = ins.add_attachment("Subject of email", "Body of attachment email", "/home/rohit/Downloads/SIH-certificate.pdf")
    
    # ins.send_email(email_send.split(';'), data = body)
    filepaths = ["/home/rohit/Downloads/SIH-certificate.pdf", "/home/rohit/Pictures/tp.png", "/home/rohit/Pictures/Unsplash/nice.jpg", "/home/rohit/index.html"]
    for filepath in filepaths:
        print(mimetypes.MimeTypes().guess_type(filepath)[0])

