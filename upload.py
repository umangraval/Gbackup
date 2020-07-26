from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
from zipfile import ZipFile
from os.path import basename
from datetime import datetime
import pyAesCrypt
from os import stat, remove
import keyring

now = datetime.now()
filename = now.strftime("%m-%d-%Y")
zipfile = filename
# print("date and time:",filename)	

# create a ZipFile object
with ZipFile(filename, 'w') as zipObj:
   # Iterate over all the files in directory
   for folderName, subfolders, filenames in os.walk("lab1"):
       for filename in filenames:
           #create complete filepath of file in directory
           filePath = os.path.join(folderName, filename)
           # Add file to zip
           zipObj.write(filePath, basename(filePath))

# encryption/decryption buffer size - 64K
bufferSize = 64 * 1024
password = keyring.get_password("PC-Backups", "backupGdrive")

backupname="backup-"+zipfile

# encrypt
with open(zipfile, "rb") as fIn:
    with open(backupname, "wb") as fOut:
        pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)

os.remove(zipfile)

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile(".mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile(".mycreds.txt")

drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    if (file1['title'] == "PC-Backups"):       
        folderid = file1['id']

f = drive.CreateFile({'parents': [{'id': folderid}]})
f.SetContentFile(backupname) 
f.Upload() 
f = None

print("Backup taken on {}".format(datetime.now()))
os.remove(backupname)

