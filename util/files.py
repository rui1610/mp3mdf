import os
import re
from shutil import copyfile
from constants.folders import FOLDER_OUTPUT
from model.constants import DELETE_SOURCE_FILES
from pathlib import Path
from fnmatch import fnmatch


def getAllMp3Files(folder, pattern: str = "*.mp3"):

    result = []

    for path, subdirs, files in os.walk(folder):
        for name in files:
            if fnmatch(name, pattern):
                print(" - found mp3 file: " + os.path.join(path, name))
                result.append(Path(os.path.join(path, name)))

    return result


def saveAudioFile(audioFile):
    try:
        audioFile.tag.save(version=(2,3,0), encoding='utf-8')
        audioFile.tag.save()
    except Exception as e:
        print("- saveAudioFile: EXCEPTION " + str(e))
        print("                 will try to fix this this by removing the frame")
        errorMessageSplit = str(e).split(":")
        frameToDelete = errorMessageSplit[1].strip()
        for fid in list(audioFile.tag.frame_set):
            if fid.decode("utf-8") in frameToDelete:
                del audioFile.tag.frame_set[fid]
        audioFile.tag.save(version=(2,3,0),encoding='utf-8')


#################################################################
def moveFile(audioFile, sourceFile):

    artist = audioFile.tag.artist
    title = audioFile.tag.title
    counterImages = len(audioFile.tag.images)

    filenameOnly = os.path.basename(sourceFile)
    filenameBase = os.path.splitext(filenameOnly)[0]

    if artist is not None:
        artist = artist.strip()
    if title is not None:
        title = title.strip()
    else:
        title = filenameBase

    # textWithoutBrackets = re.sub("[\(\[].*?[\)\]]", "", filenameBase).strip()

    newFilename = None
    if counterImages > 0:
        folderDestinationNew = Path(FOLDER_OUTPUT, "ready", normalizeName(artist)).resolve()
        newFilename = Path(folderDestinationNew, normalizeName(artist) + " - " + normalizeName(title) + ".mp3").resolve()
    else:
        folderDestinationNew = Path(FOLDER_OUTPUT, "noCoverImageFound").resolve()
        newFilename = Path(folderDestinationNew, filenameOnly).resolve()

    try:
        path = os.path.dirname(newFilename)

        if not os.path.exists(path):
            os.makedirs(path)

        fileExists = os.path.isfile(newFilename)

        if (fileExists is True):
            os.remove(newFilename)

        copyfile(sourceFile, newFilename)

        if (DELETE_SOURCE_FILES is True):
            os.remove(sourceFile)
            print("- moveFile: moved file to " + str(newFilename))
    except Exception as e:
        print("- moveFile: EXCEPTION " + str(e))
        audioFile = None

    return None


def normalizeName(name: str):
    result = re.sub(r'[^\w\s]', '', name)
    result = result.lower()
    result = result.replace("  ", " ")
    return result
