#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\sampleUtil.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.collapseLine import CollapseLine

def GetHorizCollapsableCont(parent, width = 250, height = 250, bgColor = (1.0, 1.0, 1.0, 0.1)):
    mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=width, height=height)
    return _GetHorizCollapsableCont(mainCont, width, bgColor)


def _GetHorizCollapsableCont(mainCont, width, bgColor):
    rightCont = Container(name='rightCont', parent=mainCont, align=uiconst.TORIGHT, width=0)
    CollapseLine(parent=mainCont, align=uiconst.TORIGHT, collapsingSection=rightCont, collapsingSectionWidth=width / 2, isCollapsed=True, padLeft=8, settingKey='UI_catalog_collapse_line3')
    cont = Container(name='toAllCont', parent=mainCont, align=uiconst.TOALL, clipChildren=True, bgColor=bgColor)
    return cont


def GetVertCollapsableCont(parent, width = 250, height = 250, bgColor = eveColor.MATTE_BLACK):
    mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=width, height=height)
    return _GetVertCollapsableCont(mainCont, height, bgColor)


def _GetVertCollapsableCont(mainCont, height, bgColor):
    bottomCont = Container(name='bottomCont', parent=mainCont, align=uiconst.TOBOTTOM, height=0)
    CollapseLine(parent=mainCont, align=uiconst.TOBOTTOM, collapsingSection=bottomCont, collapsingSectionWidth=height / 2, isCollapsed=True, padTop=8, padRight=28, settingKey='UI_catalog_collapse_line4')
    cont = Container(name='toAllCont', parent=mainCont, align=uiconst.TOALL, clipChildren=True, bgColor=bgColor)
    return cont


def GetCollapsableCont(parent, width = 250, height = 250, bgColor = eveColor.MATTE_BLACK):
    mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=width, height=height)
    cont = _GetVertCollapsableCont(mainCont, height, bgColor=None)
    return _GetHorizCollapsableCont(cont, width, bgColor=bgColor)
