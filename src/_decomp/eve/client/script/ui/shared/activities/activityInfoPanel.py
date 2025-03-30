#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\activities\activityInfoPanel.py
import blue
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui.control.eveEdit import Edit
from eve.client.script.ui.shared.activities.activitiesUIConst import ACTIVITY_INFO_BUTTON_BACKGROUND, ACTIVITY_INFO_CLOSE_BUTTON_POS, ACTIVITY_INFO_FOOTER_HEIGHT, ACTIVITY_INFO_MAIN_CONTAINER_HEIGHT, ACTIVITY_INFO_OPEN_STORE_BUTTON_POS
from eve.common.lib import appConst
from localization import GetByLabel

class ActivityInfoPanel(Container):

    def ApplyAttributes(self, attributes):
        super(ActivityInfoPanel, self).ApplyAttributes(attributes)
        self.service = sm.GetService('activities')
        self.ConstructMain()
        self.ConstructFooterParent()
        self.ConstructFooter()
        self.browser = Edit(parent=self.mainCont, padding=appConst.defaultPadding, readonly=1, opacity=1.0)
        self.browser.AllowResizeUpdates(0)
        self.browser.sr.window = self.mainCont

    def UpdateHTML(self, info):
        if self.state in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
            blue.pyos.synchro.Yield()
            self.browser.LoadHTML(info)

    def ConstructMain(self):
        self.mainCont = Container(parent=self, name='footerMain', align=uiconst.TOTOP, bgColor=Color.BLACK, height=ACTIVITY_INFO_MAIN_CONTAINER_HEIGHT, opacity=1.0)

    def ConstructFooterParent(self):
        self.footerParent = Container(parent=self, name='footer', align=uiconst.TOBOTTOM, bgColor=Color.BLACK, height=ACTIVITY_INFO_FOOTER_HEIGHT, opacity=1.0)

    def ConstructFooter(self):
        Button(name='returnButton', parent=self.footerParent, align=uiconst.CENTER, pos=ACTIVITY_INFO_CLOSE_BUTTON_POS, label=GetByLabel('UI/NewActivitiesWindow/Close'), func=self.OnCloseClicked, texturePath=ACTIVITY_INFO_BUTTON_BACKGROUND)
        Button(name='openStoreButton', parent=self.footerParent, align=uiconst.CENTER, pos=ACTIVITY_INFO_OPEN_STORE_BUTTON_POS, func=self.OpenStore, label=GetByLabel('UI/NewActivitiesWindow/GoToBuy'), texturePath=ACTIVITY_INFO_BUTTON_BACKGROUND)

    def OnCloseClicked(self, *args):
        self.service.OnActivityInfoCloseClicked()

    def OpenStore(self, *args):
        self.service.StartAction()
