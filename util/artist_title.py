from model.constants import SEPARATOR_ARTIST_TITLE
import re
from pathlib import Path
import os


def getArtistAndTitleFromFilename(filename):
    artist = None
    title = None

    filenameOnly = Path(filename).stem
    filenameBase = os.path.splitext(filenameOnly)[0]
    text = filenameBase
    counterSeparator = text.count(SEPARATOR_ARTIST_TITLE)
    if counterSeparator == 1:
        artist, title = text.split(SEPARATOR_ARTIST_TITLE)
    if counterSeparator > 1:
        posLastSeparator = text.rindex(SEPARATOR_ARTIST_TITLE)
        artist = text[posLastSeparator:]
        title = text[:posLastSeparator+len(SEPARATOR_ARTIST_TITLE)]

    # Remove all text in brackets
    if title:
        title = re.sub("[\(\[].*?[\)\]]", "", title).strip()
    if artist:
        artist = re.sub("[\(\[].*?[\)\]]", "", artist).strip()

    # Remove all text that has things like "feat."
    deletionList = ["feat."]
    for entry in deletionList:
        if artist:
            if entry in artist:
                pos = artist.rindex(entry)
                artist = artist[:pos]

    if artist is None and title is None:
        artist = filenameBase

    return [artist, title]
