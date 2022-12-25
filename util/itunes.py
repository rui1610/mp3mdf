from util.files import saveAudioFile
import urllib.parse
import time
import requests
from util.fuzzy import fuzzyCheckIfGoodResult
from util.artist_title import getArtistAndTitleFromFilename
from util.string_cleaner import clean_song_name
from util. metadata import getImageDescriptionForType


def sendRequestToItunes(searchString):

    maximumResults = 200
    searchString = searchString.replace(':', '/')

    term = {"term": searchString}

    termUrlEncoded = urllib.parse.urlencode(term)
    req_string = 'https://itunes.apple.com/search?' + termUrlEncoded + '&entity=musicTrack&type=songs&limit=' + str(maximumResults)

    try:
        # Adding 3 seconds of delay here to not exceed iTunes API access limits of 20 API calls per minute
        # Checkout https://developer.apple.com/forums/thread/66399?page=2 for some more information
        time.sleep(3)
        response = requests.get(req_string)
        if response.status_code == 200:
            response = response.json()
            return response
        else:
            return None

    except Exception as e:
        print(" - addItunesCoverArt: EXCEPTION found")
        print("   >> request: " + req_string)
        print("   >> " + str(e))
        return None


def getMetadataFromItunes(audioFile):
    result = None
    matches = []

    [artist, title] = getArtistAndTitleFromFilename(audioFile.path)

#    artist = audioFile.tag.artist
#    title = audioFile.tag.title
    searchTerm = ""
    if artist and title:
        searchTerm = artist + " " + title
    else:
        searchTerm = clean_song_name(artist)

    response = sendRequestToItunes(searchTerm)

    if response is not None and "results" in response:
        for thisResponse in response['results']:
            artistFound = thisResponse['artistName']
            titleFound = thisResponse['trackName']
            matchRatio = fuzzyCheckIfGoodResult(artist, title, artistFound, titleFound)
            if matchRatio > 90:
                thisResponse["matchRatio"] = matchRatio
                matches.append(thisResponse)

    if len(matches) == 0:
        [artistFilename, titleFilename] = getArtistAndTitleFromFilename(audioFile.path)
        if artistFilename != artist or titleFilename != title:
            response = sendRequestToItunes(artistFilename + " " + titleFilename)

            if response is not None and "matches" in response:
                for thisResponse in response['results']:
                    artistFound = thisResponse['artistName']
                    titleFound = thisResponse['trackName']
                    matchRatio = fuzzyCheckIfGoodResult(artist, title, artistFound, titleFound)
                    if matchRatio > 90:
                        thisResponse["matchRatio"] = matchRatio
                        matches.append(thisResponse)

    result = getBestMatch(audioFile, matches)

    return result


def getBestMatch(audioFile, response):

    result = None

    maxMatch = 0
    for entry in response:
        match = entry["matchRatio"]
        if match > maxMatch:
            maxMatch = match
            result = entry
    return result


def addMetadataFromItunes(audioFile):

    thisResponse = getMetadataFromItunes(audioFile)
    if thisResponse is not None:

        audioFile.tag.artist = thisResponse["artistName"]
        audioFile.tag.title = thisResponse["trackName"]

        if ('collectionName' in thisResponse):
            audioFile.tag.album = thisResponse['collectionName']

        if ('trackNumber' in thisResponse):
            audioFile.tag.track = thisResponse['trackNumber']

        if ('trackCount' in thisResponse):
            audioFile.tag.track_total = thisResponse['trackCount']

        if ('discCount' in thisResponse):
            audioFile.tag.disc = thisResponse['discCount']

        if ('releaseDate' in thisResponse):
            audioFile.tag.releaseDate = thisResponse['releaseDate']
        if ('artistViewUrl' in thisResponse):
            audioFile.tag.artistViewUrl = thisResponse['artistViewUrl']

        if ('collectionViewUrl' in thisResponse):
            audioFile.tag.collectionViewUrl = thisResponse['collectionViewUrl']

        if ('trackTimeMillis' in thisResponse):
            audioFile.tag.trackTimeMillis = thisResponse['trackTimeMillis']

        if ('primaryGenreName' in thisResponse):
            audioFile.tag.primaryGenreName = thisResponse['primaryGenreName']
            audioFile.tag.genre = thisResponse['primaryGenreName']

        # comment = {"itunes-trackid" :  thisResponse['trackId'],"itunes-collectionid": thisResponse['collectionId'],"itunes-previewurl":thisResponse['previewUrl']}
        # thisComment = str(dictToString(comment).encode("utf-8"))
        audioFile.tag.comments.set("")

        cover = getITunesCoverBig(thisResponse)
        icon = getITunesCoverSmall(thisResponse)
        # https://eyed3.readthedocs.io/en/latest/eyed3.id3.html#eyed3.id3.frames.ImageFrame
        # audiofile.tag.images.set(0, cover, 'image/jpg', u"othercover")
        imageType = 3
        audioFile.tag.images.set(imageType, cover, 'image/jpg', getImageDescriptionForType(imageType))
        imageType = 1
        audioFile.tag.images.set(imageType, icon, 'image/jpg', getImageDescriptionForType(imageType))
        # audiofile.tag.images.set(2, icon, 'image/jpg', u"othericon")

        saveAudioFile(audioFile)


def getITunesCoverBig(response):
    urlFromAPI = response['artworkUrl100']
    url = urlFromAPI.replace("/source/100x100bb.jpg", "/source/3000x3000bb.jpg")

    return requests.get(url, stream=True).raw.data


def getITunesCoverSmall(response):
    url = response['artworkUrl30']
    return requests.get(url, stream=True).raw.data
