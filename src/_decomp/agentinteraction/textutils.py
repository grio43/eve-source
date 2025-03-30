#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\textutils.py
import re
from eveservices.menu import GetMenuService
from utillib import KeyVal

def fix_text(text):
    text = text.replace('\r\n', '')
    text = text.replace('\n', '')
    text = text.strip()
    while text.endswith('<br>'):
        text = text[:-len('<br>')]

    text = text.replace('font color = ', 'font color=')
    text = text.replace('font color =', 'font color=')
    text = fix_color_tags(text)
    return text


def fix_color_tags(text):
    color_format1 = '#[a-fA-F0-9]{6}'
    color_format2 = '"#[a-fA-F0-9]{6}"'
    for cf in (color_format1, color_format2):
        colors_to_fix = re.findall('<font color=%s>' % cf, text)
        for c in colors_to_fix:
            match = re.search(cf, c)
            if match:
                color_value = match.group()
                color_value = color_value.strip('"').strip('#')
                text = text.replace(c, '<font color=0xFF%s>' % color_value)

    return text


def get_menu_for_item(reward_item):
    if reward_item.is_blueprint_copy():
        bpDdata = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(reward_item.type_id, original=False, runsRemaining=reward_item.get_runs_remaining(), materialEfficiency=reward_item.get_material_level(), timeEfficiency=reward_item.get_productivity_level())
        abstractInfo = KeyVal(fullBlueprintData=bpDdata)
    else:
        abstractInfo = None
    return GetMenuService().GetMenuFromItemIDTypeID(None, reward_item.type_id, includeMarketDetails=True, abstractInfo=abstractInfo)
