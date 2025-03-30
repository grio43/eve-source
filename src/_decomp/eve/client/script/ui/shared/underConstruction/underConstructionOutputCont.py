#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\underConstruction\underConstructionOutputCont.py
import evetypes
import mathext
import trinity
from carbonui import const as uiconst, TextAlign, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorarc import VectorArc
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelSmall
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.shared.underConstruction.util import GetProgressFromQty
from localization import GetByLabel
ARC_RADIUS_1 = 145
ARC_RADIUS_2 = 205
ARC_RADIUS_3 = 320
ARC_RADIUS_4 = 520

class UnderConstructionOutputCont(Container):
    default_name = 'underConstructionOutputCont'
    default_width = 400
    default_height = 400

    def ApplyAttributes(self, attributes):
        super(UnderConstructionOutputCont, self).ApplyAttributes(attributes)
        self.constructedTypeID = attributes.constructedTypeID
        self._showIcon = attributes.showIcon
        self.ConstructIcon()
        self.ConstructLabels()
        self.ConstructGauges()
        self.ConstructArcs()

    def ConstructIcon(self):
        if not self._showIcon:
            return
        typeIcon = Sprite(parent=self, pos=(0, 0, 64, 64), align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        iconFrame = Sprite(parent=self, pos=(0, 0, 80, 80), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/underConstruction/iconFrame.png')
        sm.GetService('photo').GetIconByType(typeIcon, self.constructedTypeID)

    def ConstructLabels(self):
        l = EveLabelLarge(parent=self, align=uiconst.CENTER, text=evetypes.GetName(self.constructedTypeID), width=200, textAlign=TextAlign.CENTER, top=-ARC_RADIUS_1)
        l.top = -ARC_RADIUS_1 - l.height / 2 - 10
        parentGrid = LayoutGrid(parent=self, name='parentGrid', align=uiconst.CENTERBOTTOM, columns=1, top=10)
        progressCont = ContainerAutoSize(parent=parentGrid, name='progressCont', align=uiconst.CENTER)
        self.beforeProgress = EveLabelLarge(name='beforeProgress', parent=ContainerAutoSize(parent=progressCont, name='beforeProgressCont', align=uiconst.TOLEFT), align=uiconst.CENTER, text='0')
        progressCont.height = max(self.beforeProgress.height, 16)
        self.arrowSprite = Sprite(parent=ContainerAutoSize(parent=progressCont, name='arrowSprite', align=uiconst.TOLEFT), pos=(0, 0, 16, 16), align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/underConstruction/arrowRight.png', state=uiconst.UI_DISABLED)
        self.afterProgress = EveLabelLarge(name='afterProgress', parent=ContainerAutoSize(parent=progressCont, name='afterProgressCont', align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, text='')
        label = EveLabelSmall(parent=parentGrid, align=uiconst.CENTERBOTTOM, text=GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/Progress'), color=TextColor.SECONDARY)

    def ConstructGauges(self):
        self.mainGauge = GaugeCircular(parent=self, name='mainGauge', colorStart=eveColor.CRYO_BLUE, colorEnd=eveColor.CRYO_BLUE, radius=145, align=uiconst.CENTER, lineWidth=7, colorBg=(0, 0, 0, 0))
        self.wndGauge = GaugeCircular(parent=self, name='wndGauge', colorStart=eveColor.SILVER_GREY, colorEnd=eveColor.SILVER_GREY, radius=145, align=uiconst.CENTER, lineWidth=7, colorBg=(0, 0, 0, 0))

    def ConstructArcs(self):
        VectorArc(parent=self, align=uiconst.CENTER, radius=ARC_RADIUS_1, fill=False, lineWidth=0.5)
        VectorArc(parent=self, align=uiconst.CENTER, radius=ARC_RADIUS_2, fill=False, lineWidth=0.32, opacity=0.5)
        VectorArc(parent=self, align=uiconst.CENTER, radius=ARC_RADIUS_3, fill=False, lineWidth=0.25, opacity=0.5)
        VectorArc(parent=self, align=uiconst.CENTER, radius=ARC_RADIUS_4, fill=False, lineWidth=0.2, opacity=0.5)
        sprite = Sprite(parent=self, pos=(0, 0, 440, 440), align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/underConstruction/underConstructionLines.png', textureSecondaryPath='res:/UI/Texture/classes/DynamicItem/bgGlowRing.png', spriteEffect=trinity.TR2_SFX_MODULATE, state=uiconst.UI_DISABLED, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.0)
        Sprite(parent=self, pos=(0, 0, 440, 440), align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/underConstruction/underConstructionLines.png', opacity=0.2)
        animations.FadeTo(sprite, startVal=1.0, endVal=2.5, duration=2.6, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        animations.MorphVector2(sprite, 'scaleSecondary', startVal=(0.5, 0.5), endVal=(1.0, 1.0), duration=2.6, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)

    def UpdateProgress(self, currentQtyByTypeID, qtyByTypeIdInWnd, qtyRequiredByTypeID):
        currentProgress = round(float(GetProgressFromQty(currentQtyByTypeID, qtyRequiredByTypeID)), 3)
        totalRequiredQty = sum(qtyRequiredByTypeID.values())
        if sum(currentQtyByTypeID.values()) < totalRequiredQty:
            currentProgress = mathext.clamp(currentProgress, 0, 0.999)
        if qtyByTypeIdInWnd:
            qtyByTypeIdAfterDeposit = {}
            for typeID in qtyRequiredByTypeID:
                afterDepositQty = currentQtyByTypeID.get(typeID, 0) + qtyByTypeIdInWnd.get(typeID, 0)
                if afterDepositQty:
                    qtyByTypeIdAfterDeposit[typeID] = afterDepositQty

            afterDepositProgress = round(float(GetProgressFromQty(qtyByTypeIdAfterDeposit, qtyRequiredByTypeID)), 3)
            if sum(qtyByTypeIdAfterDeposit.values()) < totalRequiredQty:
                afterDepositProgress = mathext.clamp(afterDepositProgress, 0, 0.999)
            before = GetByLabel('UI/Common/Formatting/PercentageDecimal', percentage=100 * currentProgress)
            after = GetByLabel('UI/Common/Formatting/PercentageDecimal', percentage=100 * afterDepositProgress)
        else:
            afterDepositProgress = 0
            before = GetByLabel('UI/Common/Formatting/PercentageDecimal', percentage=100 * currentProgress)
            after = ''
            self.afterProgress.display = False
        self.beforeProgress.text = before
        self.afterProgress.text = after
        self.afterProgress.display = bool(after)
        self.arrowSprite.display = bool(after)
        self.mainGauge.SetValue(currentProgress)
        self.wndGauge.SetValue(afterDepositProgress)
