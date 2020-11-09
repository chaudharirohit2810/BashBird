# TermMail

## General Info:

Termmail is terminal based email client that lets you send and view emails from terminal. The app is written in python3 and uses socket programming under the hood to connect IMAP (to receive emails) and SMTP (to send emails) servers.

## Features:

-   Complete **terminal** based experience
-   Support for gmail, outlook and coep email account
-   Authenticate securely using SSL and STARTTLS
-   Send emails to multiple recipients.
-   Add multiple attachments (pdf, zip, images supported)
-   Multiple mailboxes
-   View emails by selecting mailbox
-   Delete emails
-   Download email attachments

## Getting Started:

#### Prerequisites:

1. Python3
2. Linux

#### Installing:

1. Install all the required dependencies:
    ```sh
    pip3 install -r requirements.txt
    ```

#### Usage:

1. Start using the app:
    ```sh
    python3 main.py
    ```

#### Instructions:

1. Use the app in maximize window mode for optimal experience
2. [Check the IMAP](https://support.google.com/mail/answer/7126229?hl=en) is enabled for your gmail account
3. Follow login instructions page to login using your gmail account

> The app was tested on python version 3.8 and linux environment
