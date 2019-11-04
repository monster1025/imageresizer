import sys
import getopt
import os
import platform
import time

from PIL import Image
from PIL.ExifTags import TAGS

maxImgFileSizeKb = os.getenv('MAX_IMG_FILE_SIZE', 1500)
quality = os.getenv('QUALITY', 90)
divideSize = os.getenv('DIVIDE_SIZE', 90)
folderToProcess = os.getenv('FOLDER', './img/')
sleepTime = os.getenv('SLEEP', 60)

def main():
	while True:
	    findandresize(folderToProcess, maxImgFileSizeKb)
	    print("Sleeping {}".format(sleepTime))
	    time.sleep(sleepTime)

def findandresize(dir='.', maxImgFileSizeKb=1500):
    files = []
    counter = 1
    for r, d, f in os.walk(dir):
        for file in f:
            fileLower = file.lower()
            if '.jpg' in fileLower or '.jpeg' in fileLower or '.png' in fileLower:
                filePath=os.path.join(r, file)
                fileSizeKb=int(os.path.getsize(filePath)/1024)
                if (fileSizeKb>maxImgFileSizeKb):
                    process_image(filePath, fileSizeKb, counter)
                counter=counter+1

def process_image(filePath, fileSizeKb, counter):
    img = Image.open(filePath)
    exif = img._getexif()
    model=get_exif_field(exif,'Model')
    date=get_exif_field(exif, 'DateTime')
    creation_date=get_creation_date(filePath)
    if (date == None):
        date=creation_date
    # print_exif(exif)
    resize_image(filePath, img, divideSize, quality)
    newFileSizeKb=int(os.path.getsize(filePath)/1024)
    print("[{} kB - {} kB] {} {}".format(fileSizeKb, newFileSizeKb, date, filePath.lower()))

def resize_image(filePath, img, divideSize, quality):
    exif_bin = img.info['exif']
    width, height = img.size
    img = img.resize((int(width / 100 * divideSize),int(height / 100 * divideSize)),Image.ANTIALIAS)
    img.save(filePath, exif=exif_bin, quality=quality)

def get_exif_field(exif,field):
  for (k,v) in exif.items():
     if TAGS.get(k) == field:
        return v

def print_exif(exif):
  for (k,v) in exif.items():
     print("{}: {}".format(TAGS.get(k), v))

def get_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

if __name__ == "__main__":
    main()
