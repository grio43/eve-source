#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\event_window\reward_icon.py
from eve.client.script.ui.control.itemIcon import ItemIcon
import eveformat
import eveui

class RewardIcon(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.no_align
    default_width = 52
    default_height = 52

    def __init__(self, reward, **kwargs):
        super(RewardIcon, self).__init__(**kwargs)
        eveui.Frame(bgParent=self, cornerSize=9, opacity=0.05, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png')
        icon = ItemIcon(parent=self, align=eveui.Align.center, height=40, width=40, typeID=reward.typeID)
        if reward.amount > 1:
            amount_container = eveui.ContainerAutoSize(parent=icon, align=eveui.Align.bottom_right, bgColor=(0, 0, 0, 0.5), padLeft=-3, padRight=-3, padTop=-1, left=4, top=1, idx=0)
            eveui.EveLabelSmallBold(parent=amount_container, align=eveui.Align.center, text=eveformat.number_readable_short(reward.amount))
