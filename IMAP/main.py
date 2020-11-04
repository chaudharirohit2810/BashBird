from socket import *
import ssl
import quopri
import re
import unicodedata
import os
import base64
import getpass
import html
from dotenv import load_dotenv
from bs4 import BeautifulSoup


# Functions             Functionality
# -----------------------------------------------------------------------------------------------------------
# Constructor           Logs in to the imap server using provided email and pasword
# get_mailboxes         Gets all the mailboxes available for user.
# select_mailbox        Selects particular mailbox to use
# fetch_email_headers   Fetches number of email headers from selected mailbox
# get_boundary_id       Get boundary id of body
# fetch_whole_body      Fetch body of selected email

class IMAP:
    '''Class which does all the part of IMAP Protocol

    Arguements: \t
    email: User email \t
    password: User password\t
    imap_server: Url of imap server (default: gmail)\t
    debugging: Utility variable to print sent and received messages
    '''

    # <------------------------------------------------------Variables------------------------------------------>
    # Main socket which does all the work
    __main_socket = None

    __email = ""
    __password = ""

    # Default Messages

    __AUTH_MSG = "a01 LOGIN"  # Authentication message
    __MAIL_NEW_LINE = "\r\n"

    # TODO: Create a dictionary of imap servers and port numbers
    __SSL_PORT = 993  # Port for gmail imap server
    __HOST = ''
    __TIMEOUT = 15  # 15 seconds for now

    # Dictionary keys
    __success = 'success'
    __msg = 'msg'

    __debugging = False

    # <-----------------------------------------------------Constructor------------------------------------------>

    def __init__(self, email, password, imap_server="imap.gmail.com", debugging=False):
        self.__email = email
        self.__password = password
        self.__HOST = imap_server
        self.__debugging = debugging

        try:
            # Connect to imap server
            self.__connect()
        except Exception as e:
            print(e)

    # <----------------------------------------------Private functions------------------------------------------->

    # <!-------------------------------------------Connection--------------------------------------------------->
    def __connect(self):
        '''Connect to IMAP Server'''

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
            raise Exception(
                "Something Went Wrong! Failed to connect to imap server")
        # Login after connection
        self.__login()

    def __ssl_connect(self):
        '''To wrap socket in SSL'''

        context = ssl.create_default_context()
        host = self.__HOST
        self.__main_socket = context.wrap_socket(
            self.__main_socket, server_hostname=host)

    # <!--------------------------------------------Authentication-------------------------------------------->

    def __login(self):
        '''Login to imap server'''

        # Tell imap server for authentication
        message = self.__AUTH_MSG + " " + self.__email + \
            " " + self.__password + self.__MAIL_NEW_LINE
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

    def get_mailboxes(self):
        '''To get all the available mail boxes'''

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
        return folders

    def select_mailbox(self, name):
        '''To select particular mail box

            Arguments \t
            name: Name of mailbox
        '''

        command = 'a02 SELECT {folder_name}{new_line}'.format(
            folder_name=name, new_line=self.__MAIL_NEW_LINE)
        self.__main_socket.send(command.encode())
        msg = ""
        success = True

        # Receive the response
        while 1:
            temp_msg = self.__main_socket.recv(1024).decode()
            msg += temp_msg
            flag = False
            for line in temp_msg.splitlines():
                # print(line)
                words = line.split()
                try:
                    if words[1] == "BAD" or words[1] == "NOT":
                        success = False
                        raise Exception("Failed to select mailbox")
                    elif words[1] == "OK" and (words[2] == "[READ-WRITE]" or words[2] == "[READ-ONLY]"):
                        # print(words)
                        flag = True
                        break
                except:
                    pass
            if flag:
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

    def close_mailbox(self):
        '''To deselect the selected mailbox'''

        try:
            command = "a02 CLOSE"
            code, msg = self.__send_encoded_msg(command)
            if code == "OK":
                return True
            else:
                return False
        except:
            pass

    def fetch_email_headers(self, start, count=1):
        '''To fetch email subject, mail from and date

            Arguements \t
            start: Start position from which to fetch \t
            count: Number of emails to fetch (default: 1)
        '''

        try:
            command = "a02 FETCH " + str(start - count) + ":" + str(start) + \
                " (FLAGS BODY[HEADER.FIELDS (DATE SUBJECT FROM)])" + \
                self.__MAIL_NEW_LINE
            self.__main_socket.send(command.encode())

            # Get the whole output from server
            # is_attachment is true as no need to check for attachment
            success, msg = self.__get_whole_message()
            print(msg)
            emails = []
            # If the request success then parse the header
            if success:
                msg = self.__separate_mail_headers(msg)

                for index, item in enumerate(msg):
                    decoded_email = self.__decode_mail_headers(item)
                    decoded_email['index'] = start - count + index
                    emails.insert(0, decoded_email)

                return emails
            # If the request fails then return error
            else:
                raise Exception("Failed to fetch email! Please try again!!")
        except:
            raise Exception("Failed to fetch email! Please try again!!")

    def get_boundary_id(self, index):
        '''To get boundary id of body

            Arguements \t
            index: index of email 
        '''

        try:
            # Get the boundary id to separate different bodies
            command_boundary_id = "a02 FETCH " + str(index) + \
                " (BODY[HEADER.FIELDS (Content-Type)])" + self.__MAIL_NEW_LINE
            self.__main_socket.send(command_boundary_id.encode())
            success, msg = self.__get_whole_message()
            if success:
                main_header = '\n'.join(
                    line for line in msg.splitlines()[1:-2])
                boundary_id = None
                boundary_key = "boundary="
                if main_header.find(boundary_key) == -1:
                    return None
                boundary_id = main_header[main_header.find(
                    boundary_key) + len(boundary_key):]
                boundary_id = boundary_id[:main_header.find(';')]
                return boundary_id
        except:
            return None

    def fetch_text_body(self, index):
        '''To fetch text body of email

            Arguements \t
            index: index of email 
        '''

        try:
            filenames = self.get_body_structure(index)
            is_attachment_present = False
            if len(filenames) != 0:
                is_attachment_present = True
            # Fetch the body
            command_body = "a02 FETCH " + str(index) + \
                " (BODY[1])" + self.__MAIL_NEW_LINE
            self.__main_socket.send(command_body.encode())
            # As attachment is not required
            success, msg = self.__get_whole_message()
            if success:
                main = '\n'.join(line for line in msg.splitlines()[
                                 1:-1]).strip('\r\t\n')
                try:
                    if main.splitlines()[1].lower().startswith("content-type:"):
                        multipart_boundary = main.splitlines()[0][2:]
                        body_list = self.__get_email_body_list(
                            multipart_boundary, main)
                        main = ""
                        for item in body_list:
                            header, item = self.__separate_body(item)
                            headers = self.__get_body_headers(header)
                            item = self.__get_cleaned_up_body(headers, item)
                            main += item + "\n"
                except:
                    pass

                main = self.__extract_text_from_html(main)
                temp_body = ""
                for line in main.splitlines():
                    try:

                        formatted_line = ' '.join(word for word in line.split()
                                                  if not word.startswith("="))
                    except:
                        pass
                    temp_body += formatted_line + "\n"
                main = temp_body.strip('\r\t\n')

                return {
                    'body': main,
                    'is_attachment': is_attachment_present,
                    'filename': filenames
                }
            else:
                raise Exception(
                    "Something went wrong! Body not fetched properly")
        except:
            raise Exception("Something went wrong! Body not fetched properly")

    def get_body_structure(self, index):
        '''To get attachment names

            Arguements \t
            index: index of email 
        '''

        # Fetch the body
        command_body = "a02 FETCH " + str(index) + \
            " (BODYSTRUCTURE)" + self.__MAIL_NEW_LINE
        try:
            self.__main_socket.send(command_body.encode())
            success, msg = self.__get_whole_message()
            if not success:
                raise Exception("Something went wrong")
            filenames = []
            key = '"FILENAME"'
            res = [i for i in range(len(msg)) if msg.startswith(key, i)]
            for i in res:
                temp = msg[i:]
                temp = temp[:temp.find(')')]
                filename = temp.split()[1]
                filename = filename.replace('"', '')
                filenames.append(filename)

            return filenames
        except Exception as e:
            print(e)
            return []

    def download_attachment(self, index):
        '''To download attachments, Attachments are downloaded in downloads folder by default

            Arguements \t
            index: index of email 
        '''

        try:
            boundary_id = self.get_boundary_id(index)
            # Fetch the body
            command_body = "a02 FETCH " + str(index) + \
                " (BODY[text])" + self.__MAIL_NEW_LINE
            self.__main_socket.send(command_body.encode())
            success, msg = self.__get_whole_message()
            if boundary_id == None or not success:
                raise Exception("hi")

            body_list = self.__get_email_body_list(boundary_id, msg)
            username = getpass.getuser()
            dir_path = "/home/" + username + "/Downloads/"
            msg = "File downloaded in downloads folder"
            if not os.path.isdir(dir_path):
                dir_path = "/home/" + username + "/"
                msg = "File downloaded in home folder"

            for item in body_list:
                header, main = self.__separate_body(item)
                headers = self.__get_body_headers(header)
                try:
                    if headers[0].lower().startswith("video/") or headers[0].lower().startswith("image/") or headers[0].lower().startswith("application/"):
                        success, filename = self.__get_attachment_file_name(
                            header)

                        filename = filename.replace('"', '')
                        if not success:
                            raise Exception("Hi")

                        file_path = dir_path + filename
                        attach = open(file_path, 'wb')
                        content = base64.b64decode(main)
                        attach.write(content)
                except:
                    pass
            return msg
        except Exception as e:
            print(e)
            raise Exception("Failed to download file! Please try again!!")

    def delete_email(self, index):
        '''To delete mail

            Arguements \t
            index: index of email 
        '''
        command = "a02 STORE " + \
            str(index) + " +FLAGS (\\Deleted)" + self.__MAIL_NEW_LINE
        self.__main_socket.send(command.encode())
        success, msg = self.__get_whole_message()
        if success:
            command = "a02 EXPUNGE" + self.__MAIL_NEW_LINE
            self.__main_socket.send(command.encode())
            success, msg = self.__get_whole_message()
            if success:
                number_of_mails = 0
                # Get the number of mails in mailbox
                lines_arr = msg.splitlines()
                for item in lines_arr:
                    try:
                        tokens = item.split(" ")
                        if tokens[2] == "EXISTS":
                            number_of_mails = int(tokens[1])
                    except:
                        continue
                return number_of_mails
            else:
                raise Exception("Something went wrong! Please try again")
        else:
            raise Exception("Something went wrong! Please try again")

    # <-----------------------------------------------Utils----------------------------------------------------->

    def __send_encoded_msg(self, message):
        ''' Utility function to send encoded message to imap server'''

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

    def __get_whole_message(self):
        '''To get whole reply back from the server'''

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

    # <!------------------------------------------------Base Mail Headers---------------------------------------->

    def __separate_mail_headers(self, msg):
        '''Get individual mails from received'''

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

    def __extract_text_from_encoded_words_syntax(self, encoded_words):
        '''Decode subject if it is in encoded words syntax'''

        try:
            temp = encoded_words[2:]
            # Get the charset from encoded subject
            i1 = temp.find("?")
            charset = temp[:i1].lower()
            temp = temp[i1:]

            # Get the encoding type
            encoding = temp[1].upper()
            # Get the main text
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

    def __decode_mail_headers(self, msg):
        '''To separate subject, from and date from imap header'''

        lines_arr = msg.splitlines()
        index = 0
        subject = ""
        date = ""
        mail_from = ""
        subject_key = "subject:"
        date_key = "date:"
        from_key = "from:"

        # Separate subject from returned header
        sub_index = 0
        for index, line in enumerate(lines_arr):
            if line.lower().startswith(subject_key):
                sub_index = index
                break
        subject = lines_arr[sub_index][len(subject_key):]
        for line in lines_arr[sub_index + 1:]:
            if line.lower().startswith(date_key) or line.lower().startswith(from_key):
                break
            subject += line
        subject = subject.strip()

        # Separate date from header
        date_index = 0
        for index, line in enumerate(lines_arr):
            if line.lower().startswith(date_key):
                date_index = index
                break
        date = lines_arr[date_index][len(date_key):]
        for line in lines_arr[date_index + 1:]:
            if line.lower().startswith(subject_key) or line.lower().startswith(from_key):
                break
            date += line
        date = date.strip()

        # Separate mail_from from header
        from_index = 0
        for index, line in enumerate(lines_arr):
            if line.lower().startswith(from_key):
                from_index = index
                break
        mail_from = lines_arr[from_index][len(date_key):]
        for line in lines_arr[from_index + 1:]:
            if line.lower().startswith(subject_key) or line.lower().startswith(date_key):
                break
            mail_from += line
        mail_from = mail_from.strip()

        main_subject = ""
        # Check if the subject is in encoded words syntax
        if subject.startswith("=?"):
            # Normalize the data to ascii
            while subject.startswith("=?"):
                output, ending_index = self.__extract_text_from_encoded_words_syntax(
                    subject)
                main_subject += output
                subject = subject[ending_index:]
        else:
            main_subject = subject

        main_mail_from = ""
        # Check if the date is in encoded words syntax
        if mail_from.startswith("=?"):
            # print(date)
            while mail_from.startswith("=?"):
                output, ending_index = self.__extract_text_from_encoded_words_syntax(
                    mail_from)
                main_mail_from += output
                mail_from = mail_from[ending_index:]
        main_mail_from += mail_from
        return {'Subject': main_subject, 'Date': date, 'From': main_mail_from}

    # <!-------------------------------------------- Body Utils --------------------------------------------------------->

    def __get_boundary_indices(self, boundary_id, msg):
        '''To get start indices of boundary_id'''

        # Replace quotes in boundary_id
        boundary_id = boundary_id.replace('"', '')
        # Add -- add the start of boundary_id (Present in imap_header)
        boundary_id = "--" + boundary_id
        res = [i for i in range(len(msg)) if msg.startswith(boundary_id, i)]
        # Return the array
        return res

    def __get_email_body_list(self, boundary_id, msg):
        '''Separate bodies from email'''

        # Find all the occurunce of boundary_id
        boundary_indices = self.__get_boundary_indices(boundary_id, msg)
        body_list = []
        i = 0
        while i < len(boundary_indices) - 1:
            # Select body between two occurunces of boundary_id
            temp_msg = msg[boundary_indices[i]:boundary_indices[i + 1]].strip()

            body_list.append(
                '\n'.join(line for line in temp_msg.splitlines()[1:]))
            i += 1
        # Return all the bodies present in email
        return body_list

    def __separate_body(self, body):
        '''Separate header and main content of body'''

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

    def __get_body_headers(self, header):
        '''Get body headers'''

        content_type = ""
        content_encoding = ""
        content_type_key = "content-type:"
        content_encoding_key = "content-transfer-encoding:"
        boundary_key = "boundary="
        boundary = None
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
                content_encoding = line[line.find(
                    content_encoding_key) + len(content_encoding_key):].strip()

        return content_type, content_encoding, boundary

    def __get_attachment_file_name(self, header):
        '''To get the attachment file name from header'''

        key = "filename="
        for line in header.splitlines():
            index = line.find(key)
            if index != -1:
                start = index + len(key) + 1
                name = line[start:]
                end_index = name.find(";")
                if end_index == -1:
                    name = name[:-1]
                else:
                    name = name[:-2]
                return True, name
        return False, "File does not exits"

    def __get_cleaned_up_body(self, header, body):
        '''To get text from body according to content-type and content-transfer-encoding'''

        text = body
        if header[1].lower().strip() == "base64":
            text = base64.b64decode(text).decode('utf-8')
        text = self.__extract_text_from_html(text)
        try:
            text = quopri.decodestring(text).decode()
        except Exception as e:
            pass
        ans = '\n'.join(line for line in text.splitlines()
                        if line).strip('\r\t\n')
        return ans

    def __extract_text_from_html(self, body):
        '''To get text from html'''

        text = ""
        try:
            soup = BeautifulSoup(body, "lxml")
            for extras in soup(['script', 'style']):
                extras.extract()
            text = soup.get_text()
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
    num = imap.select_mailbox(folders[0])
    result = imap.fetch_text_body(num - 5)
