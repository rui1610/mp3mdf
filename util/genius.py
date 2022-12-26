import requests
import re
import os
from lyricsgenius import Genius
from util.files import saveAudioFile
from util.metadata import hasArtist, hasLyrics, hasTitle

GENIUS_ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')

# if GENIUS_ACCESS_TOKEN and len(GENIUS_ACCESS_TOKEN) > 0:

genius = Genius(GENIUS_ACCESS_TOKEN)
genius.excluded_terms = ["(Remix)", "(Live)"]
genius.remove_section_headers = True
genius.skip_non_songs = True


def prepareSearchUrl(audioFile):

    artist = str(audioFile.tag.artist.lower())
    title = str(audioFile.tag.title).lower()

    song = re.sub('[^0-9a-zA-Z]+', '', title)
    artist = re.sub('[^0-9a-zA-Z]+', '', artist)
    url = "http://www.azlyrics.com/lyrics/" + artist + "/" + song + ".html"

    return url


def getLyricsFromUrlContent(content):

    result = None

    findStart = "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
    startLyrics = content.find(findStart) + len(findStart)
    if startLyrics > len(findStart):
        lyricsText = content[startLyrics:]
        findEnd = "</div>"
        endLyrics = lyricsText.find(findEnd)
        theseLyrics = lyricsText[:endLyrics]
        theseLyrics = theseLyrics.replace("\r\n", "\n")
        theseLyrics = theseLyrics.replace("<br>", "")
        result = theseLyrics

    return result


def deleteLyricsIfContainingHtmlTags(audioFile):
    lyrics = audioFile.tag.lyrics

    tagsToCheck = ["</title>", "</script>", "</head>"]

    htmlFound = False
    for lyric in lyrics:
        text = lyric.text

        for tag in tagsToCheck:
            if tag in text:
                htmlFound = True

        if htmlFound is True:
            audioFile.tag.lyrics.set("")
            saveAudioFile(audioFile)


def getSongInfoFromGenius(audioFile):
    if GENIUS_ACCESS_TOKEN is None or GENIUS_ACCESS_TOKEN == "":
        print("Missing GENIUS_ACCESS_TOKEN as env variable. Skipping search for lyrics on genius API.")
        return None

    try:
        song = genius.search_song(title=audioFile.tag.title, artist=audioFile.tag.artist, get_full_info=True)

        if song is not None:
            return song
        else:
            return None
    except Exception as e:
        print("WARNING: Timeout execption on genius API. No lyrics collected: " + str(e))

        return None


def addMetadataFromGenius(audioFile):

    if GENIUS_ACCESS_TOKEN and len(GENIUS_ACCESS_TOKEN) > 0:
        if hasArtist(audioFile) and hasTitle(audioFile):
            if hasLyrics(audioFile) is False:
                metadata = getSongInfoFromGenius(audioFile)
                if metadata is not None:
                    lyrics = metadata.lyrics
                    audioFile.tag.lyrics.set('"' + lyrics + '"')
            saveAudioFile(audioFile)
    else:
        print("Can't add lyrics as GENIUS_ACCESS_TOKEN env variable wasn't set.")
