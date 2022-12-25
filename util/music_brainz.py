from util.artist_title import getArtistAndTitleFromFilename
import musicbrainzngs
import requests
from util.metadata import getImageDescriptionForType
from util.files import saveAudioFile
from util.fuzzy import fuzzyCheckIfGoodResult

MB_USERAGGENT_LINK = "https://ourNewMusikApp.de"
MB_USERAGGENT_NAME = "Rui's new app"
MB_USERAGGENT_VERSION = "0.4"


def getMetadataFromMusicbrainz(audioFile):
    result = None
    matches = []

    artist = audioFile.tag.artist
    title = audioFile.tag.title
    try:
        response = sendRequestToMusicbrainz(artist, title)

        if response is not None and "recording-list" in response:
            for thisResponse in response['recording-list']:
                artistFound = thisResponse["artist-credit-phrase"]
                titleFound = thisResponse["title"]
                # fitScore = thisResponse["ext:score"]
                matchRatio = fuzzyCheckIfGoodResult(artist, title, artistFound, titleFound)
                if matchRatio > 90:
                    thisResponse["matchRatio"] = matchRatio
                    matches.append(thisResponse)
    except Exception as e:
        print(" - addItunesCoverArt: EXCEPTION found")
        print("   >> " + str(e))
        return matches

    if len(matches) == 0:
        [artistFilename, titleFilename] = getArtistAndTitleFromFilename(audioFile.path)
        if artistFilename != artist or titleFilename != title:
            try:
                response = sendRequestToMusicbrainz(artistFilename, titleFilename)

                if response is not None and "recording-list" in response:
                    for thisResponse in response['recording-list']:
                        artistFound = thisResponse["artist-credit-phrase"]
                        titleFound = thisResponse["title"]
                        # fitScore = thisResponse["ext:score"]
                        matchRatio = fuzzyCheckIfGoodResult(artist, title, artistFound, titleFound)
                        if matchRatio > 90:
                            thisResponse["matchRatio"] = matchRatio
                            matches.append(thisResponse)
            except Exception as e:
                print(" - addItunesCoverArt: EXCEPTION found")
                print("   >> " + str(e))
                return matches
    result = getBestMatch(audioFile, matches)

    return result


def sendRequestToMusicbrainz(artist, title):

    maximumResults = 200
    musicbrainzngs.set_useragent(MB_USERAGGENT_NAME, MB_USERAGGENT_VERSION, MB_USERAGGENT_LINK)
    response = musicbrainzngs.search_recordings(artist=artist, recording=title,  limit=maximumResults, strict=False)
    return response


def getBestMatch(audioFile, response):

    result = None
    maxMatch = 0
    for entry in response:
        match = entry["matchRatio"]
        entry["hasCover"] = False

        if ('id' in entry["release-list"][0]):
            releaseId = entry["release-list"][0]["id"]
            list = getImageList(releaseId)
            if list is not None and len(list) > 0:
                entry["hasCover"] = True

        if match > maxMatch:
            maxMatch = match
            result = entry

        # Take an entry that has a cover image (even if the match ratio is lower)
        if entry["hasCover"] is True and result["hasCover"] is False:
            return entry
        # If we have an entry already with cover images, just take that one!
        if entry["hasCover"] is True and result["hasCover"] is True:
            return entry

    return result


def addMetadataFromMusicbrainz(audioFile):

    thisResponse = getMetadataFromMusicbrainz(audioFile)
    if thisResponse is not None:

        audioFile.tag.artist = thisResponse["artist-credit-phrase"]
        audioFile.tag.title = thisResponse["title"]

        if ('release-list' in thisResponse and len(thisResponse["release-list"]) > 0):
            audioFile.tag.album = thisResponse["release-list"][0]["title"]

            if ('date' in thisResponse["release-list"][0]):
                audioFile.tag.releaseDate = thisResponse["release-list"][0]["date"]
            if ('id' in thisResponse["release-list"][0]):
                # releaseId = thisResponse["release-list"][0]["id"]
                cover = getMusicbrainzCover(thisResponse, "cover")
                if cover is not None:
                    imageType = 3
                    audioFile.tag.images.set(imageType, cover, 'image/jpg', getImageDescriptionForType(imageType))
                cover = getMusicbrainzCover(thisResponse, "icon")
                if cover is not None:
                    imageType = 1
                    audioFile.tag.images.set(imageType, cover, 'image/jpg', getImageDescriptionForType(imageType))

            if ('medium-list' in thisResponse["release-list"][0]):
                if len(thisResponse["release-list"][0]["medium-list"]) > 0:
                    entryMediumList = thisResponse["release-list"][0]["medium-list"]
                    if 'track-list' in entryMediumList[0] and len(entryMediumList[0]["track-list"]) > 0:
                        if "number" in entryMediumList[0]["track-list"][0]:
                            audioFile.tag.track = entryMediumList[0]["track-list"][0]["number"]
                        if "length" in entryMediumList[0]["track-list"][0]:
                            audioFile.tag.trackTimeMillis = entryMediumList[0]["track-list"][0]["length"]

            if ('medium-track-count' in thisResponse["release-list"][0]):
                audioFile.tag.track_total = thisResponse["release-list"][0]["medium-track-count"]

            if ('medium-count' in thisResponse["release-list"][0]):
                audioFile.tag.disc = thisResponse["release-list"][0]["medium-count"]

        if ('tag-list' in thisResponse):
            tags = thisResponse["tag-list"]
            primaryGenre = None
            maxCounter = 0
            for tag in tags:
                count = int(tag["count"])
                name = tag["name"]
                if count > maxCounter:
                    primaryGenre = name
            if primaryGenre is not None:
                audioFile.tag.primaryGenreName = primaryGenre
                audioFile.tag.genre = primaryGenre
        saveAudioFile(audioFile)


def getMusicbrainzCover(response, type):

    list = getImageList(response["release-list"][0]["id"])
    if list is not None:
        urlCover = None
        urlIcon = None
        if "images" in list and len(list['images']) > 0:
            imageDetails = list['images'][0]
            if "image" in imageDetails:
                urlCover = imageDetails["image"]

            if "thumbnails" in imageDetails and "large" in imageDetails["thumbnails"]:
                urlCover = imageDetails["thumbnails"]["large"]
        if "thumbnails" in imageDetails and "small" in imageDetails["thumbnails"]:
            urlIcon = imageDetails["thumbnails"]["small"]

        if type == "icon":
            return requests.get(urlIcon, stream=True).raw.data
        else:
            return requests.get(urlCover, stream=True).raw.data
    return None


def getImageList(id):
    result = None
    musicbrainzngs.set_useragent(MB_USERAGGENT_NAME, MB_USERAGGENT_VERSION, MB_USERAGGENT_LINK)
    try:
        result = musicbrainzngs.get_image_list(id)
    except Exception:
        result = None

    return result


def getImage(id):
    result = None
    musicbrainzngs.set_useragent(MB_USERAGGENT_NAME, MB_USERAGGENT_VERSION, MB_USERAGGENT_LINK)
    try:
        result = musicbrainzngs.get_image(id)
    except Exception:
        result = None

    return result
