#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\contactsConst.py
from eve.client.script.ui import eveColor
from eve.common.lib import appConst
TAB_CONTACTS = 'contact'
TAB_CORPCONTACTS = 'corpcontact'
TAB_ALLIANCECONTACTS = 'alliancecontact'
TAB_AGENTS = 'agents'
TAB_BOOKMARKS = 'placesnew'
TAB_SEARCH = 'search'
iconByContactType = {appConst.contactAll: 'res:/UI/Texture/classes/Contacts/allContacts.png',
 appConst.contactWatchlist: 'res:/UI/Texture/classes/Contacts/buddyList.png',
 appConst.contactBlocked: 'res:/UI/Texture/classes/Contacts/blocked.png',
 appConst.contactNotifications: 'res:/UI/Texture/classes/Contacts/notifications.png'}
COLOR_ONLINE = eveColor.SUCCESS_GREEN
COLOR_OFFLINE = eveColor.DANGER_RED
