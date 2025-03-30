#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovDashboard\devIndexHints.py
from carbon.common.script.util.format import FmtAmt
import localization

def SetNormalBoxHint(box):
    boxNumber = box.boxNumber
    partialValue = box.partialValue
    level = boxNumber + 1
    if partialValue:
        perc = partialValue * 100
        hintText = localization.GetByLabel('UI/InfrastructureHub/PercentageOfLevel', perc=int(perc), level=level)
    else:
        hintText = localization.GetByLabel('UI/InfrastructureHub/LevelX', level=level)
    box.hint = hintText


def SetStrategyHint(box):
    boxNumber = box.boxNumber
    partialValue = box.partialValue
    level = boxNumber + 1
    dayList = [ str(v) for v in sm.GetService('sov').GetTimeIndexValuesInDays() ]
    hintText = localization.GetByLabel('UI/InfrastructureHub/LevelNeedsSovForDays', level=level, days=int(dayList[level - 1]))
    if partialValue:
        perc = FmtAmt(partialValue * 100)
        hintText = localization.GetByLabel('UI/InfrastructureHub/LevelNeedsSovForDaysPerc', levelText=hintText, percNumber=perc)
    box.hint = hintText
