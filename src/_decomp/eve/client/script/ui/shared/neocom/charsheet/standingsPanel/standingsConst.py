#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsConst.py
from carbonui.services.setting import UserSettingEnum
SORTED_BY_ID = 'standings_sortedByID'
SORTED_BY_STANDING_ASCENDING = 'standings_sortedAscending'
SORTED_BY_STANDING_DESCENDING = 'standings_sortedDescending'
SORTED_ALPHABETICALLY = 'standings_sortedAlphabetically'
SORTED_BY_RECENTLY_CHANGED = 'standing_sortedByRecentlyChanged'
SORT_BY_OPTIONS = (('UI/Standings/DefaultFilter', SORTED_BY_ID),
 ('UI/Standings/AscendingFilter', SORTED_BY_STANDING_ASCENDING),
 ('UI/Standings/DescendingFilter', SORTED_BY_STANDING_DESCENDING),
 ('UI/Standings/NameFilter', SORTED_ALPHABETICALLY),
 ('UI/Standings/RecentChangeFilter', SORTED_BY_RECENTLY_CHANGED))
STANDING_SORT_SETTING = UserSettingEnum('standingsSortedBy', SORTED_BY_ID, (value for _, value in SORT_BY_OPTIONS))
