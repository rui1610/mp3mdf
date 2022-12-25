
def hasArtist(audioFile):
    hasInfo = False
    if audioFile is not None:

        info = audioFile.tag.artist
        if info is not None or info != "":
            hasInfo = True
    return hasInfo


def hasCover(audioFile):
    hasInfo = False
    if audioFile is not None:
        counter = len(audioFile.tag.images)
        if counter > 0:
            hasInfo = True
    return hasInfo


def hasTitle(audioFile):
    hasInfo = False
    if audioFile is not None:
        info = audioFile.tag.title
        if info is not None or info != "":
            hasInfo = True
    return hasInfo


def hasLyrics(audioFile):
    hasLyrics = False
    if audioFile is not None:
        for lyric in audioFile.tag.lyrics:
            text = lyric.text
            if text is not None and len(text) > 0:
                hasLyrics = True
    return hasLyrics


def getImageDescriptionForType(type):
    description = "dummy"
    if type == 8:
        description = "artist"
    if type == 4:
        description = "back_cover"
    if type == 10:
        description = "band"
    if type == 19:
        description = "band_logo"
    if type == 17:
        description = "fish"
    if type == 11:
        description = "composer"
    if type == 9:
        description = "conductor"
    if type == 15:
        description = "during_performance"
    if type == 14:
        description = "during_recording"
    if type == 3:
        description = "front_cover"
    if type == 1:
        description = "icon"
    if type == 18:
        description = "illustration"
    if type == 7:
        description = "lead_artist"
    if type == 5:
        description = "leaflet"
    if type == 12:
        description = "lyricist"
    if type == 20:
        description = "publisher_logo"
    if type == 6:
        description = "media"
    if type == 0:
        description = "other"
    if type == 2:
        description = "other_icon"
    if type == 13:
        description = "recording_location"

    return description
