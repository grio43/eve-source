#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\widgets\healthwidgets.py
import threadutils
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
import evetypes
import localization
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from progression.client.const import WIDGET_TEXT_BOLD_WHITE, COLOR_UI_HIGHLIGHTING
from progression.client.widgets.basewidget import BaseWidget
import mathext
HEALTHBAR_WIDTH = 28

class HealthBarSection(Container):

    def ApplyAttributes(self, attributes):
        super(HealthBarSection, self).ApplyAttributes(attributes)
        healthWidth = attributes.healthPercent * HEALTHBAR_WIDTH
        self.health = Container(name='health', parent=self, align=uiconst.TOLEFT, width=healthWidth, bgColor=(1.0, 1.0, 1.0, 0.4))
        self.damage = Container(name='damage', parent=self, align=uiconst.TOLEFT, width=HEALTHBAR_WIDTH, bgColor=(158 / 256.0,
         11 / 256.0,
         14 / 256.0,
         1.0))


class ShieldHealthBar(HealthBarSection):

    def ApplyAttributes(self, attributes):
        super(ShieldHealthBar, self).ApplyAttributes(attributes)


class ArmorHealthBar(HealthBarSection):

    def ApplyAttributes(self, attributes):
        super(ArmorHealthBar, self).ApplyAttributes(attributes)


class HullHealthBar(HealthBarSection):

    def ApplyAttributes(self, attributes):
        super(HullHealthBar, self).ApplyAttributes(attributes)


class HealthBar(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(HealthBar, self).ApplyAttributes(attributes)
        shieldDamage, armordamage, hullDamage, _, _ = attributes.damageState
        self.hull = HullHealthBar(name='HullHealthBar', parent=self, align=uiconst.TOLEFT, width=HEALTHBAR_WIDTH, padRight=2, clipChildren=True, healthPercent=mathext.clamp(round(hullDamage, 2), 0.0, 1.0))
        self.armor = ArmorHealthBar(name='ArmorHealthBar', parent=self, align=uiconst.TOLEFT, width=HEALTHBAR_WIDTH, padRight=2, clipChildren=True, healthPercent=mathext.clamp(round(armordamage, 2), 0.0, 1.0))
        self.shield = ShieldHealthBar(name='ShieldHealthBar', parent=self, align=uiconst.TOLEFT, width=HEALTHBAR_WIDTH, padRight=2, clipChildren=True, healthPercent=mathext.clamp(round(shieldDamage, 2), 0.0, 1.0))

    def UpdateHealth(self, damageState):
        if damageState is None:
            return
        shieldDamage, armordamage, hullDamage, _, _ = damageState
        animations.MorphScalar(self.shield.health, 'width', self.shield.health.width, shieldDamage * HEALTHBAR_WIDTH, duration=0.4)
        animations.MorphScalar(self.armor.health, 'width', self.armor.health.width, armordamage * HEALTHBAR_WIDTH, duration=0.4)
        animations.MorphScalar(self.hull.health, 'width', self.hull.health.width, hullDamage * HEALTHBAR_WIDTH, duration=0.4)


class HealthWidget(BaseWidget):
    __notifyevents__ = ['OnDamageStateChange', 'OnBallAdded']

    def ApplyAttributes(self, attributes):
        super(HealthWidget, self).ApplyAttributes(attributes)
        self.label = None
        self.itemIDs = attributes.widget_state
        self.waitText = attributes.static_data.wait_text
        self.healthBarsByItemID = {}
        self.itemIdToTypeID = {}
        self.updateTimers = []
        self._ConstructDamageUI()
        sm.RegisterNotify(self)

    def OnBallAdded(self, slimItem):
        if slimItem.itemID not in self.itemIdToTypeID:
            self.itemIdToTypeID[slimItem.itemID] = slimItem.typeID
        if slimItem.itemID in self.itemIDs:
            if slimItem.itemID in self.healthBarsByItemID:
                self.UpdateHealthBars(slimItem.itemID)
            else:
                self._ConstructDamageUI()

    def OnDamageStateChange(self, shipID, damageState):
        if shipID in self.itemIDs:
            self.UpdateHealthBars(shipID, damageState)

    @threadutils.throttled(0.4)
    def UpdateHealthBars(self, itemID, damageState = None):
        healthBar = self.healthBarsByItemID.get(itemID, None)
        if healthBar:
            if not damageState:
                ballpark = sm.GetService('michelle').GetBallpark()
                damageState = ballpark.GetDamageState(itemID)
            healthBar.UpdateHealth(damageState)
            itemName = self.GetItemName(itemID)
            if self.label.GetText() != itemName:
                self._ConstructDamageUI()

    def GetItemName(self, itemID):
        itemType = self.itemIdToTypeID.get(itemID, None)
        if itemType is None:
            ball = sm.GetService('michelle').GetBall(itemID)
            if ball:
                itemType = ball.typeID
                self.itemIdToTypeID[itemID] = itemType
        if itemType is not None:
            return evetypes.GetName(itemType)
        return localization.GetByLabel('UI/Progression/Identifying')

    def _ConstructDamageUI(self):
        self.mainContainer.Flush()
        self.healthBarsByItemID = {}
        height = 0
        if self.itemIDs:
            ballpark = sm.GetService('michelle').GetBallpark()
            for itemID in self.itemIDs:
                if itemID in self.healthBarsByItemID:
                    continue
                healthCont = Container(name='healthCont', parent=self.mainContainer, align=uiconst.TOTOP, height=16, width=252)
                damageState = ballpark.GetDamageState(itemID)
                if damageState is None:
                    labelCls = self.GetLabelClass()
                    self.label = labelCls(name='entityName', parent=healthCont, align=uiconst.TOPLEFT, text=self.waitText, padRight=4)
                    textWidth, textHeight = self.label.GetAbsoluteSize()
                    height += textHeight
                    continue
                labelCls = self.GetLabelClass()
                self.label = labelCls(name='entityName', parent=healthCont, align=uiconst.TOPLEFT, text=self.GetItemName(itemID), padRight=4, wrapMode=uiconst.WRAPMODE_FORCEWORD, maxWidth=140)
                healthBar = HealthBar(name='HealthBar', parent=healthCont, align=uiconst.CENTERRIGHT, damageState=damageState, height=8)
                self.healthBarsByItemID[itemID] = healthBar
                self.updateTimers.append(AutoTimer(400, self.UpdateHealthBars, itemID))
                textWidth, textHeight = self.label.GetAbsoluteSize()
                height += textHeight

        self.parent.height = height

    def GetDynamicHighlightedItemIDs(self):
        return self.healthBarsByItemID.keys()

    def Close(self):
        for timer in self.updateTimers:
            timer.KillTimer()

        sm.UnregisterNotify(self)
        super(HealthWidget, self).Close()

    def OnMouseEnter(self, *args):
        if self.label:
            self.label.SetTextColor(COLOR_UI_HIGHLIGHTING)
            super(HealthWidget, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        if self.label:
            self.label.SetTextColor(WIDGET_TEXT_BOLD_WHITE)
            super(HealthWidget, self).OnMouseExit(*args)
