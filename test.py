import getpass
import os

user = getpass.getuser()
# Mail directory path
dir_path = '/home/'+user+'/.termmail'

print(dir_path)
os.mkdir(dir_path)
