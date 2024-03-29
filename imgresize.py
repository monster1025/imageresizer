import sys
import getopt
import os
import platform
import time
import logging

from PIL import Image
from PIL.ExifTags import TAGS

class file_counter(object):
    def __init__(self):
        self.position = self.size = 0

    def seek(self, offset, whence=0):
        if whence == 1:
            offset += self.position
        elif whence == 2:
            offset += self.size
        self.position = min(offset, self.size)

    def tell(self):
        return self.position

    def write(self, string):
        self.position += len(string)
        self.size = max(self.size, self.position)

maxImgFileSizeKb = int(os.getenv('MAX_IMG_FILE_SIZE', 2000))
quality = int(os.getenv('QUALITY', 90))
divideSize = int(os.getenv('DIVIDE_SIZE', 90))
folderToProcess = os.getenv('FOLDER', './img/')
sleepTime = int(os.getenv('SLEEP', 60))
log = None

def main():
    while True:
        log.info('Start resizing images in {}'.format(folderToProcess))
        findandresize(folderToProcess, maxImgFileSizeKb)
        log.info("Sleeping {}".format(sleepTime))
        time.sleep(sleepTime)

def findandresize(dir='.', maxImgFileSizeKb):
    files = []
    counter = 1
    for r, d, f in os.walk(dir):
        for file in f:
            fileLower = file.lower()
            if '.jpg' in fileLower or '.jpeg' in fileLower or '.png' in fileLower:
                filePath=os.path.join(r, file)
                fileSizeKb=int(os.path.getsize(filePath)/1024)
                if (fileSizeKb>maxImgFileSizeKb):
                    # try:
                    process_image(filePath, fileSizeKb, counter, maxImgFileSizeKb)
                    # except Exception:
                    #     log.error("Error processing {}".format(filePath))
                counter=counter+1

def process_image(filePath, fileSizeKb, counter, maxImgFileSizeKb):
    img = Image.open(filePath)
    # exif = img._getexif()
    # model=get_exif_field(exif, 'Model')
    # date=get_exif_field(exif, 'DateTime')
    # creation_date=get_creation_date(filePath)
    # if (date == None):
    #     date=creation_date
    # print_exif(exif)
    resize_image(filePath, img, divideSize, quality, maxImgFileSizeKb)
    filePath = rename_file(filePath, counter)
    newFileSizeKb=int(os.path.getsize(filePath)/1024)
    log.info("[{} kB - {} kB] {}".format(fileSizeKb, newFileSizeKb, filePath))

def rename_file(filePath, counter):
    dir, file=os.path.split(filePath)
    newFilePath=os.path.join(dir, file.lower())
    os.rename(filePath, newFilePath)
    return newFilePath


def resize_image(filePath, img, divideSize, quality, maxImgFileSizeKb):
    exif_bin = None
    if 'exif' in img.info:
      exif_bin = img.info['exif']
    width, height = img.size
    img = img.resize((int(width / 100 * divideSize),int(height / 100 * divideSize)),Image.ANTIALIAS)
    current_quality = guess_quality_for_size(img, maxImgFileSizeKb*1024)
    log.info("We guess quality for file {}: {}".format(filePath, current_quality))
    img.save(filePath, exif=exif_bin, quality=current_quality)

def get_exif_field(exif,field):
  if exif == None:
    return None
  for (k,v) in exif.items():
     if TAGS.get(k) == field:
        return v

def print_exif(exif):
  for (k,v) in exif.items():
     log.info("{}: {}".format(TAGS.get(k), v))

def guess_quality_for_size(im, size, guess=70, subsampling=1, low=1, high=100):
    while low < high:
        counter = file_counter()
        im.save(counter, subsampling=subsampling, quality=guess)
        if counter.size < size:
            low = guess
        else:
            high = guess - 1
        guess = (low + high + 1) // 2
    return low

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

def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

if __name__ == "__main__":
    log = get_module_logger(__name__)
    main()

