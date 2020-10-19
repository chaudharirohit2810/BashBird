from socket import *
import ssl, quopri, re, unicodedata, os, base64
from dotenv import load_dotenv
from bs4 import BeautifulSoup


'''Class which does all the part of SMTP Protocol'''
# Functions             Functionality
#-----------------------------------------------------------------------------------------------------------
# Constructor           Logs in to the imap server using provided email and pasword
# get_mailboxes         Gets all the mailboxes available for user.
# select_mailbox        Selects particular mailbox to use 
# fetch_email_headers   Fetches number of email headers from selected mailbox
# get_boundary_id       Get boundary id of body
# fetch_whole_body      Fetch body of selected email

class IMAP:
    
    #<------------------------------------------------------Variables------------------------------------------>
    # Main socket which does all the work
    __main_socket = None


    __email = ""
    __password = ""

    # Default Messages

    __AUTH_MSG = "a01 LOGIN" # Authentication message
    __MAIL_NEW_LINE = "\r\n"


    # TODO: Create a dictionary of imap servers and port numbers
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
            raise Exception("Invalid email or password")




    # <!-------------------------------------Commands related to IMAP----------------------------------------->

    '''To get all the available mail boxes'''
    # TODO: Later add main mailbox name as arguement which will give sub mailboxes
    def get_mailboxes(self):
        # LIST command which needs to be sent to imap server
        send = 'a02 LIST "" "*"'
        self.__main_socket.settimeout(2)
        code, msg = self.__send_encoded_msg(send)
        self.__main_socket.settimeout(self.__TIMEOUT)
        if code != "OK":
            raise Exception("Not able to fetch mailboxes")

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
                name += " "
            # print(name)
            if name[:-1] != '"[Gmail]"':
                folders.append(name[:-1])


        # Return list of folders except last attribute
        return {self.__success: True, 'folders': folders}

    

    '''To select particular main box'''
    # Arguements:
    # name      Name of mailbox
    def select_mailbox(self, name):
        command = 'a02 SELECT {folder_name}{new_line}'.format(folder_name = name, new_line=self.__MAIL_NEW_LINE)
        self.__main_socket.send(command.encode())
        msg = ""
        success = True
        
        # Receive the response
        while 1:
            try:
                temp_msg = self.__main_socket.recv(1024).decode()
                msg += temp_msg
                flag = False
                for line in temp_msg.splitlines():
                    # print(line)
                    words = line.split()
                    try:
                        if words[1] == "BAD" or words[1] == "NOT":
                            success = False
                            raise Exception("Hi")
                        elif words[1] == "OK" and (words[2] == "[READ-WRITE]" or words[2] == "[READ-ONLY]"):
                            # print(words)
                            flag = True
                            break
                    except:
                        pass
                if flag:
                    break
            except Exception as e:
                # print(e)
                break
        
        
        if not success:
            raise Exception('Invalid mailbox name')
            # return {self.__success: False, 'msg': "Invalid mailbox name", 'number_of_mails': -1}
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

            return number_of_mails


    '''To deselect the selected mailbox'''
    def close_mailbox(self):
        command = "a02 CLOSE"
        code, msg = self.__send_encoded_msg(command)
        if code == "OK":
            return True
        else:
            return False

    


    '''To fetch email headers'''
    # Arguements:
    # Start: Start index of mail
    # count: Number of mails to fetch
    def fetch_email_headers(self, start, count = 1):
        command = "a02 FETCH " + str(start - count) + ":" + str(start) + \
            " (BODY[HEADER.FIELDS (DATE SUBJECT FROM)])" + self.__MAIL_NEW_LINE
        self.__main_socket.send(command.encode())
        
        # Get the whole output from server
        success, msg = self.__get_whole_message()

        emails = []
        # If the request success then parse the header
        if success:
            msg = self.__separate_mail_headers(msg)
            
            for index, item in enumerate(msg):
                decoded_email = self.__decode_mail_headers(item)
                decoded_email['index'] = start - count + index;
                emails.insert(0, decoded_email)

            return True, emails

        # If the request fails then return error
        else:
            return False, "Failed to fetch email! Please try again!!"



    '''To get boundary id of body'''
    # The boundary id can be used to separate diffent body
    # Arguements:
    # index: Index of mail to fetch
    def get_boundary_id(self, index):
        # Get the boundary id to separate different bodies
        command_boundary_id = "a02 FETCH " + str(index) + \
            " (BODY[HEADER.FIELDS (Content-Type)])" + self.__MAIL_NEW_LINE
        self.__main_socket.send(command_boundary_id.encode())
        success, msg = self.__get_whole_message()
        
        if success:
            main_header = '\n'.join(line for line in msg.splitlines()[1:-2])
            boundary_id = None
            boundary_key = "boundary="
            if main_header.find(boundary_key) == -1:
                return None

            boundary_id = main_header[main_header.find(boundary_key) + len(boundary_key):]

            boundary_id = boundary_id[:main_header.find(';')]
            
            return boundary_id



    '''To fetch whole body of email'''
    # Arguements:
    # index: Index of mail to fetch
    def fetch_whole_body(self, index):
        # Fetch the boundary id
        boundary_id = self.get_boundary_id(index)
        body = ""

        # Fetch the body
        command_body = "a02 FETCH " + str(index) + \
                " (BODY[text])" + self.__MAIL_NEW_LINE
        self.__main_socket.send(command_body.encode())
        success, msg = self.__get_whole_message()
       
        if success:
            
            # If there is no boundary id then there is simple single part text body
            if boundary_id != None:
                # boundary_id = ""
                body_list = self.__get_email_body_list(boundary_id, msg)
                
                for item in body_list:
                    header, main = self.__separate_body(item)
                    
                    headers = self.__get_body_headers(header)

                    # If the content type is multipart/arternative then it contains two alternative bodies and we need only one
                    if headers[0].lower() == "multipart/alternative":
                        # Again split the body as it contains two bodies
                        inner_body_list = self.__get_email_body_list(headers[2], item)
                        
                        try:
                            header, main = self.__separate_body(inner_body_list[0])
                            
                            headers = self.__get_body_headers(header)
                            
                            main = self.__get_cleaned_up_body(headers, main)
                        except:
                            main = ""
                            pass

                    elif headers[0].lower() in ['text/plain', 'text/html']:
                        main = self.__get_cleaned_up_body(headers, main)
                    else:
                        main = ""

                    body += main + "\n"

                return body

            else:
                msg = self.__extract_text_from_html(msg)
                msg = '\n'.join(line for line in msg.splitlines()[1:-1])
                return msg.strip('\r\t\n')
        # Return the error if request fails
        else:
            raise Exception("Something went wrong! Body not fetched properly")
       



    '''To delete mail from mailbox'''
    # Arguements:
    # index: Index of mail to fetch
    def delete_email(self, index):
        command = "a02 STORE " + str(index) + " +FLAGS (\\Deleted)"
        code, msg = self.__send_encoded_msg(command)
        if code == "OK":
            command = "a02 EXPUNGE"
            code, msg = self.__send_encoded_msg(command)
            if code == "OK":
                number_of_mails = 0
                # Again get the number of mails in mailbox
                lines_arr = msg.splitlines()
                for item in lines_arr:
                    try:
                        tokens = item.split(" ")
                        if tokens[2] == "EXISTS":
                            number_of_mails = int(tokens[1])
                    except:
                        continue

                return True, number_of_mails
            else:
                return False, 0
        else:
            return False, 0





                   


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


    
    '''To get whole reply back from the server'''
    def __get_whole_message(self):
        msg = ""
        email_results = ["OK", "NO", "BAD"]
        while 1:
            try:
                # Receive message from server
                recv_bytes = self.__main_socket.recv(1024)

                temp_msg = recv_bytes.decode(errors='ignore')
               
                # Split the lines from the received message
                lines_arr = temp_msg.splitlines()
                
                # Check if the last line contains the codes involved in imap protocol
                code1 = None
                code2 = None

                try:
                    code1 = lines_arr[-1].split(" ")[0]
                    code2 = lines_arr[-1].split(" ")[1]
                    
                except Exception as e:
                    pass

                if code1 in email_results or code2 in email_results:
                    # print(code)
                    # TODO: Check if code is ok nor not

                    # print(code, msg)
                    lines_arr.pop(-1)
                    
                    # Add other lines from array to message
                    for item in lines_arr:
                        msg += item
                        msg += self.__MAIL_NEW_LINE
                    
                    # Remove first line and last two line
                    msg = msg.splitlines()
                    # msg = msg[1: -2]
                    reply = ""
                    # Again append other elements in array
                    for index in range(len(msg)):
                        reply += msg[index]
                        if index != len(msg) - 1:
                            reply += self.__MAIL_NEW_LINE
                    
                    
                    # Return them
                    return True, reply
                msg += temp_msg
            except Exception as e:
                print(e)
                # Return the error if exception occurs
                # TODO: Later return appropriate message
                return False, "Request Failed"

    



    #<!------------------------------------------------Base Mail Headers---------------------------------------->

    '''Get individual mails from received'''
    # Arguements:
    # msg: Message returned by the server
    def __separate_mail_headers(self, msg):
        lines_arr = msg.splitlines()
        ans = []
        email = ""
        prev_start = 0
        index = 0
        while index < len(lines_arr):
            # This indicates the end of particular mail
            if lines_arr[index] == "" and lines_arr[index + 1] == ")":
                email = ""
                for item in lines_arr[prev_start + 1:index]:
                    email += item + "\n"
                prev_start = index + 2
                ans.append(email) 
            index += 1  
        return ans


    '''Decode subject if it is not in ascii'''
    def __extract_text_from_encoded_words_syntax(self, encoded_words):
        try:
            temp = encoded_words[2:]

            # Get the charset from encoded subject
            i1 = temp.find("?")
            charset = temp[:i1].lower()

            temp = temp[i1:]

            # Get the encoding type            
            encoding = temp[1].upper()
            

            # GEt the main text
            main_text = temp[3:]


            # This will be encoded string
            ending_index = main_text.find("?=")
            main_text = main_text[:ending_index]
            
            if encoding == "B":
                main_text = base64.b64decode(main_text)
            elif encoding == "Q":
                main_text = quopri.decodestring(main_text)  

            return main_text.decode(charset), encoded_words.find("?=") + 3

        except Exception as e:
            print(e)
            return encoded_words



    '''To separate subject, from and date from imap header'''
    # Arguements:
    # msg: Email header in string
    def __decode_mail_headers(self, msg):
        lines_arr = msg.splitlines()
        index = 0
        subject = ""
        date = ""
        mail_from = ""
        
        # Loop to traverse over all the lines
        while index < len(lines_arr):
            # Check if it is subject
            if lines_arr[index].lower().startswith("subject"):
                flag1 = False; flag2 = False
                is_start = True
                # To handle multiline subject
                while not flag1 and not flag2:
                    try:
                        if is_start:
                            subject += lines_arr[index][9:]
                            is_start = False
                            index += 1
                        else:
                            subject += lines_arr[index] 
                            index += 1
                        try:
                            flag1 = lines_arr[index].lower().startswith("date")
                        except: 
                            flag1 = False
                        try:
                            flag2 = lines_arr[index].lower().startswith("from")
                        except:
                            flag2 = False
                    except:
                        # End of list
                        break
            # Get Date from header
            elif lines_arr[index].lower().startswith("date"):
                date = lines_arr[index][6:]
                index += 1
            # Get mail_from from header
            elif lines_arr[index].lower().startswith("from"):
                mail_from = lines_arr[index][6:]
                index += 1
        main_subject = ""

        # Check if the subject is in encoded words syntax
        if subject.startswith("=?"):
            # Normalize the data to ascii
            while subject.startswith("=?"):
                output, ending_index = self.__extract_text_from_encoded_words_syntax(subject)
                main_subject += output
                subject = subject[ending_index:]
        else:
            main_subject = subject

        main_mail_from = ""
        # Check if the date is in encoded words syntax
        if mail_from.startswith("=?"):
            # print(date)
            while mail_from.startswith("=?"):
                output, ending_index = self.__extract_text_from_encoded_words_syntax(mail_from)
                main_mail_from += output
                mail_from = mail_from[ending_index:]
        
        main_mail_from += mail_from
                

        # print(main_subject.strip())
        return {'Subject': main_subject, 'Date': date, 'From': main_mail_from}
    


    #<!-------------------------------------------- Body Utils --------------------------------------------------------->

    '''To get start indices of boundary_id'''
    # Used to separate bodies
    # boundary_id: Boundary id of email
    # msg: Reply from imap server
    def __get_boundary_indices(self, boundary_id, msg):
        # Replace quotes in boundary_id
        boundary_id = boundary_id.replace('"', '')

        # Add -- add the start of boundary_id (Present in imap_header)
        boundary_id = "--" + boundary_id
        
        boundary_indices = []
        
        # Find all the occurunces of boundary_id and add its index to array
        boundary_indices = [i.start() for i in re.finditer(boundary_id, msg)]
        
        # Return the array
        return boundary_indices



    '''Separate bodies from email'''
    # Arguements:
    # boundary_id: Boundary id of email
    # msg: Reply from imap server
    def __get_email_body_list(self, boundary_id, msg):

        # Find all the occurunce of boundary_id
        boundary_indices = self.__get_boundary_indices(boundary_id, msg)
        body_list = []
    
        i = 0
        while i < len(boundary_indices) - 1:
            # Select body between two occurunces of boundary_id
            temp_msg = msg[boundary_indices[i]:boundary_indices[i + 1]].strip()
            
            body_list.append('\n'.join(line for line in temp_msg.splitlines()[1:]))
            i += 1
       
        # Return all the bodies present in email
        return body_list


    '''Separate header and main content of body'''
    # Arguements:
    # body: Body of mail
    def __separate_body(self, body):
        i = 0
        # Loop over lines to find CRLF
        for line in body.splitlines():
            if line == '':
                break
            i += 1

        # Lines before CRLF is header
        header = '\n'.join(line for line in body.splitlines()[:i])
        # Lines after CRLF is main content
        body = '\n'.join(line for line in body.splitlines()[i:])

        # Return the header and body
        return header, body


    '''Get body headers'''
    # Arguemnts: 
    # header: Header present in body
    # return content type and content encoding type
    def __get_body_headers(self, header):
        # print(header)
        content_type = ""
        content_encoding=""
        content_type_key = "content-type:"
        content_encoding_key = "content-transfer-encoding:"
        boundary_key = "boundary="
        boundary=None

        for line in header.splitlines():
            line = line.lower()
            
            if line.find(boundary_key) != -1:
                boundary = line[line.find(boundary_key) + len(boundary_key):]
                boundary = boundary[:boundary.find(';')]
                
            # To find the content type
            if line.find(content_type_key) != -1:
                start = line.find(content_type_key) + len(content_type_key)
                content_type = line[start:]
                content_type = content_type[:content_type.find(';')].strip()
            
            # To find the content transfer encoding
            elif line.find(content_encoding_key) != -1:
                content_encoding = line[line.find(content_encoding_key) + len(content_encoding_key):].strip()

        return content_type, content_encoding, boundary


    
    '''To get text from body according to content-type and content-transfer-encoding'''
    # Arguements:
    # header: contains content-type and content-transfer encoding
    # body: Body of mail
    def __get_cleaned_up_body(self, header, body):
        text = body
        if header[1].lower().strip() == "base64":
            text = base64.b64decode(text).decode('utf-8')
            
        
        text = self.__extract_text_from_html(text)

        try:
            text = quopri.decodestring(text).decode()       
        except Exception as e:
            pass
        
        ans = ""
        ans = '\n'.join(line for line in text.splitlines() if line)
        ans = ans.strip('\r\t\n')

        return ans



    '''To get text from html'''
    # Arguements: 
    # body: Body of mail
    def __extract_text_from_html(self, body):
        text = ""
        try:
            soup = BeautifulSoup(body, "lxml")
            for extras in soup(['script', 'style']):
                extras.extract()
            text = soup.get_text()
            # Normalize the data to ascii
            text = unicodedata.normalize("NFKD",text)
        except Exception as e:
            text = body
        ans = ""
        for line in text.splitlines():
            if line.strip() == '':
                continue
            new_line = ""
            for word in line.split(" "):
                new_line += word.strip() + " "
            ans += new_line.strip() + "\n"
        return ans




if __name__ == "__main__":
    load_dotenv('./.env')
    old_mail = os.getenv('EMAIL')
    old_pass = os.getenv('PASSWORD')
    imap = IMAP(old_mail, old_pass, debugging=True)
    folders = imap.get_mailboxes()
    # print(folders)
    num = imap.select_mailbox(folders['folders'][0])
    # print(num)
    # emails = imap.fetch_email_headers(num, 20)
    # print(emails)
    body = imap.fetch_whole_body(num - 6)
    print(body)
    # imap.delete_email(num)
    # print(imap.delete_email(1))
    # imap.delete_email(10)
    # # imap.close_mailbox()
    # num =   imap.select_mailbox(folders['folders'][2])
    # emails = imap.fetch_email_headers(num, 20)
    # print(emails)
   
