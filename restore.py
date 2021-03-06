import pyAesCrypt
from os import stat, remove
from datetime import datetime
import keyring
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, sys


# encryption/decryption buffer size - 64K
bufferSize = 64 * 1024
password = keyring.get_password("PC-Backups", "backupGdrive")

def restoreFromGoogleDrive():
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

    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folderid)}).GetList()

    restore_date = input("Enter date of backup in dd-mm-yyyy: ")
    filename = "backup-"+restore_date

    for i, file1 in enumerate(sorted(file_list, key = lambda x: x['title']), start=1):
        if (file1['title'] == filename):
            print('Downloading {} from GDrive ({}/{})'.format(file1['title'], i, len(file_list)))
            file1.GetContentFile(file1['title'])

def decryptGooleDriveZip(dest):
    # get encrypted file size
    try:
        encFileSize = stat(filename).st_size

        restorefilename = dest+"/restore-"+filename+".zip"
        # decrypt
        with open(filename, "rb") as fIn:
            try:
                with open(restorefilename, "wb") as fOut:
                    # decrypt file stream
                    pyAesCrypt.decryptStream(fIn, fOut, password, bufferSize, encFileSize)
                    remove(filename)
                    print("Restored file {} at {}".format(filename, datetime.now()))
            except ValueError:
                # remove output file on error
                print("Corrupted file")
                remove(filename)
    except:
        print("backup not found")

def decryptLocalZip(zipPath, dest):
    # get encrypted file size
    try:
        encFileSize = stat(zipPath).st_size

        restorefilename = dest+"/restore-"+zipPath.split("/")[-1]+".zip"
        # decrypt
        with open(zipPath, "rb") as fIn:
            try:
                with open(restorefilename, "wb") as fOut:
                    # decrypt file stream
                    pyAesCrypt.decryptStream(fIn, fOut, password, bufferSize, encFileSize)
                    print("Restored file {} at {}".format(zipPath, datetime.now()))
            except ValueError:
                # remove output file on error
                print("Corrupted file")
    except:
        print("backup not found")

print("Restore backup from\n[1] Google Drive\n[2] Local Storage")
choice = input("Enter your choice: ")
if (choice == "1"):
    dest = input("Enter destination folder to restore (eg /path/to/folder): ")
    restoreFromGoogleDrive()
    decryptGooleDriveZip(dest)
elif(choice == "2"):
    zipPath = input("Enter source file to restore (eg /path/to/file): ")
    dest = input("Enter destination folder to restore (eg /path/to/folder): ")
    decryptLocalZip(zipPath, dest)
else:
    print("Wrong choice")
