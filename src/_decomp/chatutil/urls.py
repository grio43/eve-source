#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chatutil\urls.py
import re
import eveformat
from chatutil.filter import CleanAndHighlightText
seemsURL = re.compile('\\b\n        (\n            (\n                (https?://|www\\d{0,3}[.])           # Starts with http(s) or www with optional number\n                [a-zA-Z0-9\\-\\.]+\\.[a-zA-Z]{2,63}     # Followed by *. and .* with 2 to 63 characters\n            )\n            |                                       # or\n            (\n                https?://                           # Starts with http(s)\n                \\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}  # Followed by ip number\n            )\n        )\n        (:\\d{1,6})?                                 # Optional port number\n        (\n            (/([^\\s]+)?)                            # Must continue with / before we eat up optional non-space\n            |\n            /?                                      # or may end with single /\n        )\n        ', re.X)
alreadyURLOrTag = re.compile('(<a .*?/a>|<url.*?/url>|<.*?>)')

def LinkURLs(text):
    idx = 0
    parseParts = []
    match = alreadyURLOrTag.search(text)
    while match:
        start, end = match.span()
        parse = text[idx:start]
        if parse:
            parseParts.append((1, parse))
        notParse = text[start:end]
        parseParts.append((0, notParse))
        match = alreadyURLOrTag.search(text, end)
        idx = end

    leftOver = text[idx:]
    if leftOver:
        parseParts.append((1, leftOver))
    retText = ''
    for parseFlag, parseText in parseParts:
        if parseFlag == 0:
            cleanText = CleanTextInsideTags(parseText)
            retText += cleanText
            continue
        normalizedText = parseText
        match = seemsURL.search(normalizedText)
        idx = 0
        while match:
            start, end = match.span()
            url = normalizedText[start:end]
            while url[-1] in ',.':
                url = url[:-1]
                end -= 1

            if not url.startswith('http'):
                url = 'http://' + url
            urlText = parseText[start:end]
            urlText = CleanAndHighlightText(urlText)
            retText += parseText[idx:start] + '<url=' + url + '>' + urlText + '</url>'
            match = seemsURL.search(normalizedText, end)
            idx = end

        cleanText = CleanAndHighlightText(parseText[idx:])
        retText += cleanText

    return retText


def CleanTextInsideTags(parseText):
    withoutLinks = eveformat.strip_tags(parseText, tags=['url', 'a'])
    cleanTextWithoutLinks = CleanAndHighlightText(withoutLinks)
    return eveformat.replace_text_ignoring_tags(parseText, withoutLinks, cleanTextWithoutLinks)
