import unidecode
from fuzzywuzzy import fuzz


def fuzzyCheckIfGoodResult(artistSearch, titleSearch, artistFound, titleFound):

    if artistSearch:
        artistSearch = unidecode.unidecode(artistSearch.lower())
    if titleSearch:
        titleSearch = unidecode.unidecode(titleSearch.lower())
    artistFound = unidecode.unidecode(artistFound.lower())
    titleFound = unidecode.unidecode(titleFound.lower())
    # log.debug("Checkout match")

    # token_Sort_Ratio_artist = fuzz.token_sort_ratio(artistSearch , artistFound)
    # log.debug("ratio artist >" + artistSearch + "<, >" + artistFound + "< = " + str(token_Sort_Ratio_artist))
    # token_Sort_Ratio_title = fuzz.token_sort_ratio(titleSearch , titleFound)
    # log.debug("ratio title  >" + titleSearch + "<, >" + titleFound + "< = " + str(token_Sort_Ratio_title))

    searchTerm = ""
    if artistSearch and titleSearch:
        searchTerm = artistSearch + " " + titleSearch
    else:
        searchTerm = artistSearch

    token_Sort_Ratio = fuzz.token_sort_ratio(searchTerm, artistFound + " " + titleFound)
    # log.debug("ratio title : " + str(token_Sort_Ratio))

    if token_Sort_Ratio <= 90:
        if artistSearch in artistFound:
            token_Sort_Ratio_artist_smart = fuzz.token_sort_ratio(artistFound + " " + titleSearch, artistFound + " " + titleFound)
            if token_Sort_Ratio_artist_smart > 90:
                return token_Sort_Ratio_artist_smart
        if titleSearch and titleSearch in titleFound:
            token_Sort_Ratio_title_smart = fuzz.token_sort_ratio(artistSearch + " " + titleFound, artistFound + " " + titleFound)
            if token_Sort_Ratio_title_smart > 90:
                return token_Sort_Ratio_title_smart

    return token_Sort_Ratio


#################################################################
def checkIfGoodResult(searchString, artist, title):
    result = False

    title = unidecode.unidecode(title.lower())
    artist = unidecode.unidecode(artist.lower())
    searchString = unidecode.unidecode(searchString.lower())

    artistInSearchString = False
    titleInSearchString = False

    if " - " in searchString and searchString.count(" - ") == 1:
        [myArtist, myTitle] = searchString.split(" - ")
        titleInSearchString = myTitle in title
        artistInSearchString = myArtist in artist

    else:
        artistInSearchString = artist in searchString
        titleInSearchString = title in searchString

    if (artistInSearchString is True and titleInSearchString is True):
        result = True

    return result
