#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\tooltipsUtil.py
from carbonui import uiconst, fontconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew.agencyConst import SECURITYSTATUS_LOWSEC, SECURITYSTATUS_HIGHSEC, SECURITYSTATUS_NULLSEC
from eve.common.script.util.eveFormat import FmtSystemSecStatus
from localization import GetByLabel

def ConstructNumericSecurityStatusFillLabel(securityStatus):
    mainCont, color = _ConstructSecurityStatusLabelCont(securityStatus)
    EveLabelMedium(parent=mainCont, align=uiconst.TOLEFT, text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/AsteroidBelts/SecStatusAndLower', securityStatus=securityStatus, color=Color.RGBtoHex(*color)), left=5)
    return mainCont


def ConstructTextualSecurityStatusFillLabel(securityStatus):
    mainCont, _color = _ConstructSecurityStatusLabelCont(securityStatus)
    secStatusConst = _GetAgencyConstSecurityStatus(securityStatus)
    txt = {SECURITYSTATUS_NULLSEC: GetByLabel('UI/Common/NullSec'),
     SECURITYSTATUS_LOWSEC: GetByLabel('UI/Common/LowSec'),
     SECURITYSTATUS_HIGHSEC: GetByLabel('UI/Common/HighSec')}.get(secStatusConst)
    EveLabelMedium(parent=mainCont, align=uiconst.TOLEFT, text=txt, left=5)
    return mainCont


def _GetAgencyConstSecurityStatus(securityStatus):
    if securityStatus >= 0.5:
        return SECURITYSTATUS_HIGHSEC
    elif securityStatus >= 0.1:
        return SECURITYSTATUS_LOWSEC
    else:
        return SECURITYSTATUS_NULLSEC


def _ConstructSecurityStatusLabelCont(securityStatus):
    secStatus, color = FmtSystemSecStatus(securityStatus, True)
    mainCont = ContainerAutoSize(align=uiconst.CENTERLEFT, height=16 * fontconst.fontSizeFactor, state=uiconst.UI_NORMAL, alignMode=uiconst.TOLEFT)
    Fill(parent=mainCont, align=uiconst.TOLEFT, height=16, width=16, color=color)
    return (mainCont, color)
