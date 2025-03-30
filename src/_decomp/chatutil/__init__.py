#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chatutil\__init__.py
import hashlib
import re
from filter import CleanAndHighlightText, UpdateChatFilterVariables, GetHighlightedText, ShouldHightlightBlink
from urls import LinkURLs
import inventorycommon.const as invconst
import chatutil.const as chatUtilConst
import datetimeutils
MAX_TEXT_LEN = 1024
MAX_TEXT_LEN_SAFEGUARD = 2048
showInfoComplete = re.compile("(?P<pretext>.*?<loc><url=showinfo:) # Non-greedy consomption of all text up to shoinfo tag\n                                 (?P<typeID>\\d*)                # typeID, always present\n                                 (?P<seperator>/*)              # Optional seperator, only present when itemID is\n                                 (?P<itemID>\\d*)                # optional itemID\n                                 >                              # close bracket for show info anchor\n                                 (?P<itemName>.*?)              # Supplied item name\n                                 (?P<posttext></url>)           # Close anchor. Only here to ensure the link isn't mangled.\n                                 </loc>", re.X)

def StripBreaks(txt):
    txt = txt.strip()
    while txt.endswith('<br>'):
        txt = txt[:-4]
        txt = txt.strip()

    while txt.startswith('<br>'):
        txt = txt[4:]
        txt = txt.strip()

    return txt


def GetBodyText(response):
    text = ''
    for child in response.children:
        if child.tag == 'body':
            text = child.text

    return text


def IsInvite(response):
    xElem = response.find_child_with_tag('x')
    if xElem:
        if 'xmlns' in xElem.attributes and xElem.attributes['xmlns'] == 'http://jabber.org/protocol/muc#user':
            inviteElem = xElem.find_child_with_tag('invite')
            if inviteElem:
                return True
    return False


def IsDecline(response):
    for child in response.children:
        if child.tag == 'x':
            if 'xmlns' in child.attributes and child.attributes['xmlns'] == 'http://jabber.org/protocol/muc#user':
                if child.children and child.children[0].tag == 'decline':
                    return True

    return False


def GetInviteSender(response):
    xElem = response.find_child_with_tag('x')
    if xElem:
        if 'xmlns' in xElem.attributes and xElem.attributes['xmlns'] == 'http://jabber.org/protocol/muc#user':
            inviteElem = xElem.find_child_with_tag('invite')
            if inviteElem:
                user = inviteElem.attributes.get('from', None)
                if user:
                    return user.split('@')[0]


def GetInviteReason(response):
    xElem = response.find_child_with_tag('x')
    if xElem:
        if 'xmlns' in xElem.attributes and xElem.attributes['xmlns'] == 'http://jabber.org/protocol/muc#user':
            inviteElem = xElem.find_child_with_tag('invite')
            if inviteElem:
                reasonElem = inviteElem.find_child_with_tag('reason')
                if reasonElem:
                    return reasonElem.text


def GetInvitePassword(response):
    xElem = response.find_child_with_tag('x')
    if xElem:
        if 'xmlns' in xElem.attributes and xElem.attributes['xmlns'] == 'http://jabber.org/protocol/muc#user':
            passwordElem = xElem.find_child_with_tag('password')
            if passwordElem:
                return passwordElem.text


def GetDeclineReason(response):
    for child in response.children:
        if child.tag == 'x':
            if 'xmlns' in child.attributes and child.attributes['xmlns'] == 'http://jabber.org/protocol/muc#user':
                if child.children and child.children[0].tag == 'decline':
                    invite = child.children[0]
                    if invite.children and invite.children[0].tag == 'reason':
                        return invite.children[0].text


def GetDeclineSender(response):
    for child in response.children:
        if child.tag == 'x':
            if 'xmlns' in child.attributes and child.attributes['xmlns'] == 'http://jabber.org/protocol/muc#user':
                if child.children and child.children[0].tag == 'decline':
                    user = child.children[0].attributes.get('from', None)
                    if user:
                        return user.split('@')[0]


def ParseFeatureSet(response):
    result = []
    query = response.children[0]
    for child in query.children:
        if child.tag == 'feature':
            feature = child.attributes['var']
            result.append(feature)

    return result


def IsChannelPrivate(channelName):
    category = channelName.split('_')[0]
    isPrivate = category in ('private', 'player')
    return isPrivate


def GetStatusCodes(response):
    statusCodes = []
    x = response.find_child_with_tag('x')
    if x and x.attributes.get('xmlns', '') == 'http://jabber.org/protocol/muc#user':
        for c in x.children:
            if c.tag == 'status':
                code = c.attributes.get('code')
                statusCodes.append(code)

    return statusCodes


def ParseChannelName(channelName):
    category = 'public'
    count = 0
    if not channelName:
        channelName = ''
    trimmedChannelName = channelName.strip()
    countAsString = ''
    if trimmedChannelName.endswith(')'):
        ix = trimmedChannelName.rfind('(')
        if ix != -1:
            suffix = trimmedChannelName[ix + 1:-1]
            trimmedChannelName = trimmedChannelName[0:ix - 1]
            parts = suffix.split(',')
            if len(parts) == 1:
                countAsString = parts[0]
            elif len(parts) == 2:
                category = parts[0]
                countAsString = parts[1]
            else:
                countAsString = ''
    try:
        count = int(countAsString)
    except ValueError:
        trimmedChannelName = channelName
        category = 'public'

    return (trimmedChannelName, category, count)


def GetChannelId(channelName):
    normalized = channelName.strip().lower()
    m = hashlib.md5()
    m.update(normalized)
    return m.hexdigest()


def IsAuthError(response):
    isAuthError = False
    errorElement = response.find_child_with_tag('error')
    if errorElement:
        if errorElement.attributes['code'] == '401' and errorElement.attributes['type'] == 'auth':
            isAuthError = True
    return isAuthError


def GetCharacterBannnedExpiry(expiry_text):
    expiry = int(expiry_text)
    if expiry > 0:
        expiry = datetimeutils.unix_to_blue(expiry)
    return expiry


def GetErrorTextElement(response):
    errorElement = response.find_child_with_tag('error')
    if errorElement:
        return errorElement.find_child_with_tag('text')


def GetErrorType(response):
    errorElement = response.find_child_with_tag('error')
    if errorElement:
        return errorElement.attributes.get('type')


def GetErrorCode(response):
    errorElement = response.find_child_with_tag('error')
    if errorElement:
        return errorElement.attributes['code']


def GetUsersFromResponse(response):
    result = []
    queryElement = response.children[0]
    for child in queryElement.children:
        if child.tag == 'item':
            jid = child.attributes['jid']
            charid = jid.split('@')[0]
            try:
                charid = int(charid)
            except ValueError:
                pass

            result.append(charid)

    return result


def CheckAllowedAccess(charid, corpid, allianceid, allowed, blocked):
    allow = None
    set_charid = 'set_{0}'.format(charid)
    set_corpid = 'set_{0}'.format(corpid)
    set_allianceid = 'set_{0}'.format(allianceid)
    if 'all' in allowed:
        allow = 'all'
    elif 'all' in blocked:
        allow = None
    if set_allianceid in allowed:
        allow = 'allianceid'
    elif set_allianceid in blocked:
        allow = None
    if set_corpid in allowed:
        allow = 'corpid'
    elif set_corpid in blocked:
        allow = None
    if set_charid in allowed:
        allow = 'charid'
    elif set_charid in blocked:
        allow = None
    return allow


def GetChannelCategory(channel):
    return channel.split('_')[0]


def GetChannelDifferentiator(channel):
    return channel.split('_', 1)[1]


def CompleteAutoLinks(text):
    import localization
    import evetypes
    filledText = ''
    match = showInfoComplete.search(text)
    if match is None:
        return text
    while match is not None:
        pretext = match.group('pretext')
        typeID = match.group('typeID')
        seperator = match.group('seperator')
        itemID = match.group('itemID')
        itemName = match.group('itemName')
        posttext = match.group('posttext')
        groupID = evetypes.GetGroupID(typeID)
        if itemID == '' and typeID != '':
            filledName = evetypes.GetName(typeID)
        elif groupID in [invconst.groupCharacter, invconst.groupCorporation]:
            filledName = cfg.eveowners.Get(itemID).name
        elif groupID == invconst.groupSolarSystem:
            filledName = cfg.evelocations.Get(itemID).name
        elif groupID == invconst.groupStation:
            orbitName = cfg.evelocations.Get(cfg.stations.Get(itemID).orbitID).name
            longMoon = localization.GetByLabel('UI/Locations/LocationMoonLong')
            shortMoon = localization.GetByLabel('UI/Locations/LocationMoonShort')
            orbitName = orbitName.replace(longMoon, shortMoon).replace(longMoon.lower(), shortMoon.lower())
            filledName = localization.GetByLabel('UI/Chat/StationAutoLink', orbitName=orbitName)
        else:
            filledName = match.group('itemName')
        filledText += '%s%s%s%s>%s%s' % (pretext,
         typeID,
         seperator,
         itemID,
         filledName,
         posttext)
        text = text[match.span()[1]:]
        match = showInfoComplete.search(text)

    filledText = filledText + text
    return filledText


def TruncateVeryLongText(text):
    if len(text) > MAX_TEXT_LEN_SAFEGUARD:
        return text[:MAX_TEXT_LEN_SAFEGUARD - 5] + ' ...'
    return text
