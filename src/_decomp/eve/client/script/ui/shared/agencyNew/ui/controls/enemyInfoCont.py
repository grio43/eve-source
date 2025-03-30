#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\enemyInfoCont.py
from appConst import factionUnknown
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.section import SubSectionAutoSize
from localization import GetByLabel

class EnemyInfoCont(SubSectionAutoSize):
    default_name = 'EnemyInfoCont'
    default_headerText = GetByLabel('UI/Agency/RoamingEnemies')

    def ApplyAttributes(self, attributes):
        super(EnemyInfoCont, self).ApplyAttributes(attributes)
        self.ownerID = None
        self.ownerTypeID = None
        self.enemySprite = OwnerIcon(name='enemySprite', parent=self, align=uiconst.CENTERLEFT, width=32, height=32, padding=(0, -1, 0, -1), isSmall=True)
        self.enemyLabel = EveLabelMedium(name='enemyLabel', parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)

    def Update(self, ownerID, ownerTypeID):
        self.ownerID = ownerID
        self.ownerTypeID = ownerTypeID
        if ownerID and ownerID != factionUnknown:
            enemyNameText = GetByLabel('UI/Agency/OwnerNameURL', ownerTypeID=self.ownerTypeID, ownerID=self.ownerID)
            self.enemySprite.SetOwnerID(self.ownerID)
            self.enemySprite.Show()
            self.enemyLabel.left = 40
        else:
            enemyNameText = GetByLabel('UI/Common/Unknown')
            self.enemySprite.Hide()
            self.enemyLabel.left = 0
        self.enemyLabel.SetText(enemyNameText)
        animations.FadeIn(self, duration=0.2)
