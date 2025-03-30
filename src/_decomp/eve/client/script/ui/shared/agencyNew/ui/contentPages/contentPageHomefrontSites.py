#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageHomefrontSites.py
from carbonui import uiconst
from evearchetypes import GetArchetype
from eve.common.lib import appConst
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.homefrontSiteInfoContainer import HomefrontSiteInfoContainer
import localization

class ContentPageHomefrontSites(SingleColumnContentPage):
    default_name = 'ContentPageHomefrontSites'

    def ConstructInfoContainer(self):
        self.infoContainer = HomefrontSiteInfoContainer(parent=self)

    def ConstructTooltips(self):
        archetype = GetArchetype(appConst.dunArchetypeHomefrontSites)
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=localization.GetByMessageID(archetype.titleID), tooltipPanelClassInfo=SimpleTextTooltip(text=localization.GetByMessageID(archetype.descriptionID)))
