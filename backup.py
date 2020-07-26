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
filename = now.strftime("%d-%m-%Y")
zipfile = filename
backupname="backup-"+zipfile
# print("date and time:",filename)	

def zipfiles(filename, filepath):
    # create a ZipFile object
    with ZipFile(filename, 'w') as zipObj:
    # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(filepath):
            for filename in filenames:
                #create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                # Add file to zip
                zipObj.write(filePath)

def encryptZipfile(zipfile, backupname):
    # encryption/decryption buffer size - 64K
    bufferSize = 64 * 1024
    password = keyring.get_password("PC-Backups", "backupGdrive")

    # encrypt
    with open(zipfile, "rb") as fIn:
        with open(backupname, "wb") as fOut:
            pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)

    os.remove(zipfile)

def encryptZipfileLocal(zipfile, backupname, dest):
    # encryption/decryption buffer size - 64K
    bufferSize = 64 * 1024
    password = keyring.get_password("PC-Backups", "backupGdrive")
    finaldest = dest+"/"+backupname
    # encrypt
    with open(zipfile, "rb") as fIn:
        with open(finaldest, "wb") as fOut:
            pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)
    print("Backup taken on {}".format(datetime.now()))
    os.remove(zipfile)


def googledriveUpload(backupname):
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

print("Backup to\n[1] Google Drive\n[2] Local Storage\n")
choice = input("Enter your choice: ")
if (choice == "1"):
    filepath = input("\nEnter filepath to backup: ")
    zipfiles(filename, filepath)
    encryptZipfile(zipfile, backupname)
    googledriveUpload(backupname)
elif(choice == "2"):
    filepath = input("\nEnter filepath to backup: ")
    dest = input("\nEnter destination for backup files (eg /path/to/file): ")
    zipfiles(filename, filepath)
    encryptZipfileLocal(zipfile, backupname, dest)
else:
    print("Wrong choice")

