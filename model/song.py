from dataclasses import dataclass
import eyed3
from pathlib import Path
from util.string_cleaner import clean_song_name
from util.itunes import addMetadataFromItunes
from util.music_brainz import addMetadataFromMusicbrainz
from util.genius import addMetadataFromGenius
from util.metadata import hasTitle, hasArtist, hasCover, hasLyrics


@dataclass
class Song():
    source_file: str = None
    clean_file_name: str = None
    audio_file: str = None

    def __init__(self, source_file: str):
        self.source_file = source_file
        self._setCleanFileName()
        self._getAudioFile()

    def _getAudioFile(self):
        self.audio_file = eyed3.load(self.source_file)

        if self.audio_file.tag is None:
            self.audio_file.initTag()

        if hasCover(self.audio_file) is False or hasArtist(self.audio_file) is False or hasTitle(self.audio_file) is False:
            addMetadataFromItunes(self.audio_file)

        if hasCover(self.audio_file) is False or hasArtist(self.audio_file) is False or hasTitle(self.audio_file) is False:
            addMetadataFromMusicbrainz(self.audio_file)

        if hasLyrics(self.audio_file) is False:
            addMetadataFromGenius(self.audio_file)

    def _setCleanFileName(self):
        fileName = Path(self.source_file).stem
        self.clean_file_name = clean_song_name(fileName)
