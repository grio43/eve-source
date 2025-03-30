#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\redeem\redeemUiConst.py
from carbonui.util.color import GetColor
REDEEM_BASE_COLOR = (0.6, 0.6, 0.6)
REDEEM_BACKGROUND_COLOR = (0.0, 0.0, 0.0)
REDEEM_BUTTON_BORDER_COLOR = GetColor(REDEEM_BASE_COLOR, alpha=0.4)
REDEEM_BUTTON_FILL_COLOR = GetColor(REDEEM_BASE_COLOR, alpha=0.3, brightness=0.7)
REDEEM_BUTTON_BACKGROUND_COLOR = GetColor(REDEEM_BACKGROUND_COLOR, alpha=1.0)
TEXT_COLOR = (0.9, 0.9, 0.9)
REDEEM_PANEL_BACKGROUND_COLOR = GetColor(REDEEM_BACKGROUND_COLOR, alpha=1.0)
REDEEM_WINDOW_ID = 'redeem'
OPEN_REDEEM_WINDOW_COMMAND_NAME = 'ToggleRedeemItems'
REDEEM_ICON_PATH = 'res:/ui/texture/WindowIcons/redeemingQueue.png'
REDEEM_NOTIFICATION_ID = 'newRedeemableItemsNotification'
NEW_TOKENS_UI_HIGHLIGHT = 2242
CREATION_DATE_SORT_KEY = 'createDateTime'
EXPIRY_DATE_SORT_KEY = 'expiryDateTime'
