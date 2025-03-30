#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\redeem\client\confirm.py
import eveformat
import evelink.client
import evetypes
import inventorycommon.const as invconst
import localization
from carbonui import uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.messagebox import MessageBox

def confirm_redeem(character_id, tokens, delivery_location_id, redeem_data):
    item_tokens = [ token for token in tokens if redeem_data.must_redeem_type_in_station(token) and not redeem_data.is_auto_injected(token) ]
    soulbound_tokens = [ token for token in tokens if (redeem_data.is_auto_injected(token) or evetypes.GetCategoryID(token.typeID) == invconst.categoryExpertSystems) and not redeem_data.is_skill_inserter(token.typeID) ]
    skill_points = redeem_data.get_skillpoints_redeemed([ (token.typeID, token.quantity) for token in tokens ])
    if item_tokens and soulbound_tokens and skill_points:
        return confirm_redeem_for_all(character_id, delivery_location_id, item_tokens, soulbound_tokens, skill_points)
    if item_tokens and soulbound_tokens:
        return confirm_redeem_for_items_and_soulbound(character_id, delivery_location_id, item_tokens, soulbound_tokens)
    if item_tokens and skill_points:
        return confirm_redeem_for_items_and_skill_points(character_id, delivery_location_id, item_tokens, skill_points)
    if soulbound_tokens and skill_points:
        return confirm_redeem_for_soulbound_and_skill_points(character_id, soulbound_tokens, skill_points)
    if item_tokens:
        return confirm_redeem_for_items(character_id, delivery_location_id, item_tokens)
    if soulbound_tokens:
        return confirm_redeem_for_soulbound(character_id, soulbound_tokens)
    if skill_points:
        return confirm_redeem_for_skill_points(character_id, skill_points)


def confirm_redeem_for_all(character_id, delivery_location_id, item_tokens, soulbound_tokens, skill_points):
    soulbound_item_names = [ unicode(evelink.type_link(token.typeID)) for token in soulbound_tokens ]
    return uiconst.ID_YES == uicore.Message(msgkey='RedeemConfirmSoulboundThingsAndSkillPointsAndItemsToHangar', params={'charID': character_id,
     'skillPoints': eveformat.number(skill_points, decimal_places=0),
     'infoLinks': u'<br>'.join(soulbound_item_names),
     'num': len(item_tokens),
     'location': delivery_location_id}, buttons=uiconst.YESNO, default=uiconst.ID_NO)


def confirm_redeem_for_items_and_soulbound(character_id, delivery_location_id, item_tokens, soulbound_tokens):
    soulbound_item_names = [ unicode(evelink.type_link(token.typeID)) for token in soulbound_tokens ]
    return uiconst.ID_YES == uicore.Message(msgkey='RedeemConfirmSoulboundThingsAndItemsToHangar', params={'charID': character_id,
     'infoLinks': '<br>'.join(soulbound_item_names),
     'num': len(item_tokens),
     'location': delivery_location_id}, buttons=uiconst.YESNO, default=uiconst.ID_NO)


def confirm_redeem_for_items_and_skill_points(character_id, delivery_location_id, item_tokens, skill_points):
    return uiconst.ID_YES == uicore.Message(msgkey='RedeemConfirmSkillPointsAndItemsToHangar', params={'charID': character_id,
     'skillPoints': eveformat.number(skill_points, decimal_places=0),
     'num': len(item_tokens),
     'location': delivery_location_id}, buttons=uiconst.YESNO, default=uiconst.ID_NO)


def confirm_redeem_for_soulbound_and_skill_points(character_id, soulbound_tokens, skill_points):
    soulbound_item_names = [ unicode(evelink.type_link(token.typeID)) for token in soulbound_tokens ]
    return uiconst.ID_YES == uicore.Message(msgkey='RedeemConfirmSoulboundThingsAndSkillPoints', params={'charID': character_id,
     'infoLinks': u'<br>'.join(soulbound_item_names),
     'skillPoints': eveformat.number(skill_points, decimal_places=0)}, buttons=uiconst.YESNO, default=uiconst.ID_NO)


def confirm_redeem_for_items(character_id, delivery_location_id, tokens):
    station_ids = [ token.stationID for token in tokens if token.stationID is not None ]
    if station_ids:
        stations = u'<br>'.join((cfg.evelocations.Get(station_id).name for station_id in station_ids))
        return uiconst.ID_YES == uicore.Message(msgkey='RedeemConfirmClaimMultiple', params={'char': character_id,
         'stations': stations}, buttons=uiconst.YESNO, default=uiconst.ID_NO)
    else:
        return uiconst.ID_YES == uicore.Message(msgkey='RedeemConfirmToHangar', params={'charID': character_id,
         'num': len(tokens),
         'location': delivery_location_id}, buttons=uiconst.YESNO, default=uiconst.ID_NO)


def confirm_redeem_for_soulbound(character_id, soulbound_tokens):
    item_names = [ unicode(evelink.type_link(token.typeID)) for token in soulbound_tokens ]
    return uiconst.ID_YES == uicore.Message(msgkey='RedeemConfirmSoulboundThingClaim', params={'infoLinks': '<br>'.join(item_names),
     'charID': character_id}, buttons=uiconst.YESNO, default=uiconst.ID_NO)


def confirm_redeem_for_skill_points(character_id, skill_points):
    return uiconst.ID_YES == uicore.Message(msgkey='RedeemConfirmSkillInserter', params={'charID': character_id,
     'skillPoints': eveformat.number(skill_points, decimal_places=0)}, buttons=uiconst.YESNO, default=uiconst.ID_NO)


def confirm_trash(tokens):
    return uiconst.ID_OK == create_custom_modal(title=localization.GetByLabel('UI/Redeem/TrashModalTitle'), text=localization.GetByLabel('UI/Redeem/TrashModalText', num=len(tokens)), ok_text=localization.GetByLabel('UI/Redeem/TrashModalOkButton'))


def create_custom_modal(title, text, ok_text):
    message_box = MessageBox.Open(windowID='RedeemActionMessage', parent=uicore.desktop, idx=0)
    message_box.Execute(text=text, title=title, buttons=uiconst.OKCANCEL, icon=uiconst.QUESTION, suppText=None, okLabel=ok_text)
    return message_box.ShowModal()
