#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\layer.py
import logging
from carbonui.uicore import uicore
logger = logging.getLogger(__name__)

def get_blink_layer():
    layer = _find_layer('blink')
    if layer is None:
        layer = _create_blink_layer()
    return layer


def _create_blink_layer():
    menu_layer = _find_layer('menu')
    if menu_layer is None:
        logger.warning("The uiblinker layer is being created before the menu layer. This indicates that there's something calling the uiblinker too early in the client startup.")
        index = 0
    else:
        index = menu_layer.GetOrder()
    return uicore.desktop.AddLayer(name='l_blink', idx=index)


def _find_layer(name):
    layer_name = 'l_{}'.format(name)
    for layer in uicore.desktop.children:
        if layer.name == layer_name:
            return layer
