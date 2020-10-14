### Commands that are used in Non-Authenticated State
#### CAPABILITY:
- **Syntax**: code CAPABILITY
- **Uses**: 
    - Returns the capabilities of the imap server

#### NOOP:
- **Syntax**: code NOOP
- **Uses**:
    - Just used to keep the connection between server and client alive.

#### LOGOUT:
- **Syntax**: code LOGOUT
- **Uses**:
    - To end the connection between client and server

<br></br>

### Commands that are used to go from Non-Authenticated State to Authenticated State
#### LOGIN:
- **Syntax**: code LOGIN username password (The username and password are plaintext)
- **Uses**:
    - Use of the LOGIN command over an insecure network is security risk, because anyone monitoring network traffic can obtain plaintext passwords. 
    - Only when the connection is over SSL or TLS has been started then only use LOGIN command.

<br></br>

### Commands that are used in Authenticated State:
#### SELECT:
- **Syntax**: code SELECT mailbox_name
- **Uses**:
  - Selects a mailbox so that emails in that mailbox can be accessed.
  - Only one mailbox can be selected at one time for one connection. The select automatically deselects mailboxes if multiple mailboxes are selected.
- **Response**:
  - FLAGS: Flags available for mailbox.
  - n EXISTS: Number of emails (n) in mailbox
  - m RECENT: The number of emails (m) with the \Recent flag set.
  - OK PREFIX: The PREFIX can be READ-WRITE (You can modify mailbox) or READ-ONLY(You can't modify mailbox)
- **Output**:
  > \* FLAGS (\Answered \Flagged \Draft \Deleted \Seen $NotPhishing $Phishing) \
  \* OK [PERMANENTFLAGS (\Answered \Flagged \Draft \Deleted \Seen $NotPhishing $Phishing \*)] Flags permitted. \
  \* OK [UIDVALIDITY 6] UIDs valid. \
  \* 13 EXISTS \
  \* 0 RECENT \
  \* OK [UIDNEXT 140] Predicted next UID. \
  \* OK [HIGHESTMODSEQ 2178483] \
    a02 OK [READ-WRITE] [Gmail]/Drafts selected. (Success)


#### Examine:
- **Syntax**: code EXAMINE mailbox_name
- **Uses**
  - Similar to SELECT command. The only difference is that a mailbox is opened in READ-ONLY mode.


#### CREATE:
- **Syntax**: code CREATE mailbox_name
- **Uses**:
  - To create a new mailbox. 
  - It is error to create mailbox with name INBOX. 
  - To create mailbox inside another mailbox / is used. Eg.code CREATE parent_mailbox/child_mailbox


#### DELETE:
- **Syntax**: code DELETE mailbox_name
- **Uses**:
  - To delete a mailbox 
  - All the emails in mailbox also get deleted when mailbox is deleted
  - mailboxes inside deleted mailbox are not deleted.


#### RENAME:
- **Syntax**: code RENAME old_mailbox_name new_mailbox_name
- **Uses**: 
  - To rename a mailbox
  - Hierachical mailboxes are also renamed when parent mailbox name changes.

