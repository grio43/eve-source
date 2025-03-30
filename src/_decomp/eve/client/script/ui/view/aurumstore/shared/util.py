#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\shared\util.py
import localization

def GetSortedTokens(productQuantities):
    return localization.util.Sort(productQuantities.values(), key=lambda product: product.name)
