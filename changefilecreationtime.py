import argparse
import os
from ctypes import windll, wintypes, byref, WinError
import datetime
from pathlib import PureWindowsPath

#####################################

class File():
    def __init__(self, pathToFile):
        self.path = pathToFile

    def changeCreationDate(self):
        now = datetime.datetime.utcnow()
        nowUnix = (now - datetime.datetime(1970,1,1)).total_seconds()

        timestamp = int((nowUnix * 10000000) + 116444736000000000)

        if not 0 < timestamp < (1 << 64):
            raise ValueError('Timestamp ist groeßer als 64-bit: ' + str(self.path))

        ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)

        handle = windll.kernel32.CreateFileW(str(self.path), 256, 0, None, 3, 128, None)

        if not wintypes.BOOL(windll.kernel32.SetFileTime(handle, byref(ctime), None, None)):
            raise WinError()
        
        if not wintypes.BOOL(windll.kernel32.CloseHandle(handle)):
            raise WinError()

        print('Erstellungsdatum geaendert: ' + str(self.path))

    def printPath(self):
        print(str(self.path))

#####################################
parser = argparse.ArgumentParser(description = 'Erstellungsdatum aendern')

parser.add_argument('ordner',
    help = 'Ordner der die zu aendernden Dateien enthaelt'
    )

args = parser.parse_args()

#####################################
path = PureWindowsPath(args.ordner) #'testfolder test/'

folderContent = []

for root, dirs, files in os.walk(path, topdown=True, followlinks=False):
     for afile in files:
         folderContent.append(File(PureWindowsPath(root + '\\' + afile)))

if len(folderContent) == 0:
    raise IndexError('Keine Dateien im angegbenen Ordner oder Ordner exitiert nicht')

for element in folderContent:
    element.printPath()
    element.changeCreationDate()
