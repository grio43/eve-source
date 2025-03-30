#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\neocombutton.py
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeEvent import BtnDataNodeEvent
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeNotification import BtnDataNodeNotification
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import UnseenItemsExtension
from localization import GetByLabel

class SeasonsNeocomButton(UnseenItemsExtension):

    def __init__(self, get_badge_count):
        super(SeasonsNeocomButton, self).__init__(button_data_class=BtnDataNodeNotification, get_badge_count=get_badge_count)

    @property
    def is_visible(self):
        return sm.GetService('seasonService').is_season_visible_in_agency()

    def create_button_data(self, parent):
        self.button_data = BtnDataNodeEvent(parent=parent, btnType=neocomConst.BTNTYPE_EVENT, iconPath='res:/UI/Texture/classes/Seasons/eventIcon_64x64.png', cmdName='OpenSeason', label=GetByLabel('UI/Seasons/Title'), descriptionPath='UI/Seasons/Subcaption', btnID='SeasonBtnDataNode', isRemovable=False, isBlinking=False)
        return self.button_data
