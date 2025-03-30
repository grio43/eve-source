#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\const.py
from brennivin.itertoolsext import Bundle
from notifications.client.notificationUIConst import NOTIFICATION_CENTER_PADDING_H
REGION_CHINA = 'optic'
RATING_ICONS_PATH = 'res:/UI/Texture/classes/RegionalUI/kr/'
RATING_ICONS = {1: Bundle(width=61, height=71, name='age18'),
 2: Bundle(width=61, height=71, name='violence'),
 3: Bundle(width=61, height=71, name='gambling')}
ADDICTION_WARNING_TEXT_PATH = 'UI/Regional/KR/AddictionWarning'
SESSION_PLAYTIME_TEXT_PATH = 'UI/Regional/KR/SessionPlaytime'
SPLASH_TEXT_PATH = 'UI/Regional/KR/SplashText'

def get_icon_path(icon_name):
    return RATING_ICONS_PATH + icon_name + '.png'


RATINGS_PADDING_H = NOTIFICATION_CENTER_PADDING_H
RATINGS_PADDING_TOP = 4
RATINGS_PADDING_BOTTOM = 3
RATINGS_PADDING_BETWEEN = 4

def get_ratings_width():
    number_of_icons = len(RATING_ICONS)
    total_icon_separation = max(0, number_of_icons - 1) * RATINGS_PADDING_BETWEEN
    total_icons_width = sum([ icon.width for icon in RATING_ICONS.values() ])
    total_padding = 2 * RATINGS_PADDING_H
    return total_icons_width + total_icon_separation + total_padding
