from zipfile import ZipFile
import os
from os.path import basename
from datetime import datetime
import pyAesCrypt
from os import stat, remove

now = datetime.now()
filename = now.strftime("%m-%d-%Y")
zipfile = filename
# print("date and time:",filename)	


# create a ZipFile object
with ZipFile(filename, 'w') as zipObj:
   # Iterate over all the files in directory
   for folderName, subfolders, filenames in os.walk("lab1"):
#        print(folderName, subfolders, filenames)
#        for foldername in subfolders:
#            #create complete filepath of file in directory
#            filePath = os.path.join(folderName, foldername)
#            # Add file to zip
#            zipObj.write(filePath, basename(filePath))

       for file in filenames:
           #create complete filepath of file in directory
           filePath = os.path.join(folderName, file)
           # Add file to zip
           zipObj.write(filePath)

# encryption/decryption buffer size - 64K
bufferSize = 64 * 1024
password = "password"

backupname="backup-"+zipfile

# encrypt
with open(zipfile, "rb") as fIn:
    with open(backupname, "wb") as fOut:
        pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)

os.remove(zipfile)