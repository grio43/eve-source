#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\subtitles.py
import blue
import logging
import urllib2
logger = logging.getLogger(__name__)

def GetSubtitlePathForVideo(videoPath, languageID):
    basePath = _rchop(videoPath, '.webm')
    subtitlePath = '%s_%s.srt' % (basePath, languageID)
    return subtitlePath


def _rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s


def _ParseTime(timeStr):
    import re

    def matchToMilliseconds(offset):
        return int(match.group(3 + offset)) + int(match.group(2 + offset)) * 1000 + int(match.group(1 + offset)) * 1000 * 60 + int(match.group(0 + offset)) * 1000 * 60 * 60

    match = re.match('(\\d{1,2}):(\\d{1,2}):(\\d{1,2}),(\\d{1,3})\\s+-->\\s+(\\d{1,2}):(\\d{1,2}):(\\d{1,2}),(\\d{1,3}).*', timeStr)
    if match is None:
        raise ValueError
    return (matchToMilliseconds(1), matchToMilliseconds(5))


class Subtitles(object):

    def __init__(self):
        self._subtitles = []

    def LoadSubtitleFile(self, path):
        if path.lower().startswith('res:/') or path.find(':') < 2:
            try:
                text = blue.paths.GetFileContentsWithYield(path).read()
            except (IOError, RuntimeError):
                logger.warn("Video Player: Can't load subtitles in path: %s" % path)
                return

        else:
            try:
                text = urllib2.urlopen(path).read()
            except IOError:
                return

        return text

    def PrepareSubtitles(self, text):
        text = text.decode('utf-8')
        state = 'number'
        time = ''
        subText = []
        for line in text.split('\n'):
            if state == 'number':
                state = 'time'
            elif state == 'time':
                time = line.strip()
                state = 'text'
            else:
                line = line.strip()
                if line == '':
                    try:
                        self._subtitles.append((_ParseTime(time), '\n'.join(subText)))
                    except ValueError:
                        pass

                    state = 'number'
                    subText = []
                else:
                    subText.append(line)

    def GetSubtitle(self, milliseconds):
        for time, text in self._subtitles:
            if time[0] <= milliseconds <= time[1]:
                return text

        return ''
