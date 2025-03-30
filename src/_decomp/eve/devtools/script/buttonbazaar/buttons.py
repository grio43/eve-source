#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\buttonbazaar\buttons.py
import collections
import itertools
import math
import mock
import eve.client.script.ui.shared.infoPanels.listSurroundingsBtn
import localization
from carbonui import uiconst

class Group(object):
    core = 1
    derived = 2
    primitive = 3


class ButtonData(object):

    def __init__(self, group, factory):
        self.group = group
        self.factory = factory

    def create(self):
        return self.factory()


_button_definitions = collections.defaultdict(list)

def _register(factory, group):
    global _button_definitions
    _button_definitions[group].append(ButtonData(group, factory))


def register(f):
    _register(f, Group.derived)
    return f


def register_core(f):
    _register(f, Group.core)
    return f


def register_primitive(f):
    _register(f, Group.primitive)
    return f


def iter_buttons(group = None):
    if group is None:
        it = itertools.chain(*_button_definitions.values())
    else:
        it = _button_definitions[group]
    for data in it:
        yield data


@register_core
def create_button():
    import carbonui.control.button
    return carbonui.control.button.Button(label='Button')


@register_core
def create_primary_button():
    from eve.client.script.ui.control import primaryButton
    return primaryButton.PrimaryButton(label='PrimaryButton')


@register_core
def create_text_button_with_backgrounds():
    import eve.client.script.ui.control.buttons
    return eve.client.script.ui.control.buttons.TextButtonWithBackgrounds(width=160, height=30, text='TextButtonWithBackgrounds')


@register_core
def create_toggle_button_group_button():
    import eve.client.script.ui.control.toggleButtonGroupButton
    return eve.client.script.ui.control.toggleButtonGroupButton.LegacyToggleButtonGroupButton(width=160, height=30, label='LegacyToggleButtonGroupButton')


@register_core
def create_button_icon():
    import carbonui.control.buttonIcon
    return carbonui.control.buttonIcon.ButtonIcon(width=32, height=32, iconSize=24, texturePath='res:/ui/Texture/WindowIcons/Industry.png')


@register_primitive
def create_container():
    from carbonui.primitives.container import Container
    return Container()


@register_primitive
def create_container_auto_size():
    from carbonui.primitives.containerAutoSize import ContainerAutoSize
    return ContainerAutoSize()


@register_primitive
def create_sprite():
    import carbonui.primitives.sprite
    return carbonui.primitives.sprite.Sprite()


@register_primitive
def create_glow_sprite():
    import eve.client.script.ui.control.glowSprite
    return eve.client.script.ui.control.glowSprite.GlowSprite()


@register_primitive
def create_transform():
    import carbonui.primitives.transform
    return carbonui.primitives.transform.Transform()


@register
def create_station_service_button():
    import eve.client.script.ui.shared.dockedUI.serviceBtn
    from utillib import KeyVal
    service_info = KeyVal(label='UI/StructureSettings/ServiceIndustry', texturePath='res:/ui/Texture/WindowIcons/Industry.png', stationServiceIDs=[], command='', serviceID=None, disableButtonIfNotAvailable=False)
    return eve.client.script.ui.shared.dockedUI.serviceBtn.StationServiceBtn(width=48, height=48, serviceInfo=service_info)


@register
def create_filter_button():
    import eve.client.script.ui.control.filter
    return eve.client.script.ui.control.filter.FilterButton(label=localization.GetByLabel('UI/Ledger/OreTypeFilter'))


@register
def create_crate_button():
    import eve.client.script.ui.crate.button
    return eve.client.script.ui.crate.button.CrateButton(label=localization.GetByLabel('UI/Crate/OpenLater'))


@register
def create_scanner_scan_button():
    from eve.client.script.ui.inflight.scannerFiles import scanButton
    from carbonui.uicore import uicore
    cmd = uicore.cmd.commandMap.GetCommandByName('CmdRefreshDirectionalScan')
    controller = scanButton.ScanButtonController(directional_scan_service=sm.GetService('directionalScanSvc'), service_manager=sm)
    return scanButton.ScanButton(cmd=cmd, controller=controller)


@register
def create_scanner_formation_button():
    from eve.client.script.ui.inflight.scannerFiles import scannerToolsUIComponents
    return scannerToolsUIComponents.FormationButton(launchFunc=None, width=32, height=32)


@register
def create_inflight_security_button():
    from eve.client.script.ui.inflight import shipSafetyButton
    import crimewatch.const
    from carbonui import fontconst
    return shipSafetyButton.SecurityButton(safetyLevel=crimewatch.const.shipSafetyLevelPartial, canBeModified=True, width=140 * fontconst.fontSizeFactor)


@register
def create_inflight_security_confirm_button():
    from eve.client.script.ui.inflight import shipSafetyButton
    import crimewatch.const
    return shipSafetyButton.SafetyConfirmButton(color=shipSafetyButton.SAFETY_LEVEL_DATA_MAP[crimewatch.const.shipSafetyLevelPartial].color.GetRGBA(), safetyButton=mock.Mock(), canBeModified=True)


@register
def create_dark_style_stateful_primary_button():
    import eve.client.script.ui.control.statefulButton
    from eve.client.script.ui.const import buttonConst
    controller_mock = mock.Mock()
    controller_mock.GetButtonState.return_value = buttonConst.STATE_SETDESTINATION
    controller_mock.GetButtonFunction.return_value = None
    controller_mock.IsButtonEnabled.return_value = True
    controller_mock.GetButtonTexturePath.return_value = 'res:/UI/Texture/Shared/actions/setDestination.png'
    controller_mock.GetButtonLabel.return_value = localization.GetByLabel('UI/Inflight/SetDestination')
    return eve.client.script.ui.control.statefulButton.StatefulButton(iconAlign=uiconst.TORIGHT, controller=controller_mock)


@register
def create_abyss_activate_button():
    from eve.client.script.ui.shared.abyss import activateButton
    controller_mock = mock.Mock()
    controller_mock.isReady = True
    controller_mock.isActivating = False
    controller_mock.errors = []
    controller_mock.GetText.return_value = localization.GetByLabel('UI/Abyss/Activate')
    return activateButton.ActivateButton(fixedheight=30, fixedwidth=120, controller=controller_mock)


@register
def create_asset_safety_deliver_button():
    import eve.client.script.ui.shared.assets.assetSafetyEntry
    button = eve.client.script.ui.shared.assets.assetSafetyEntry.DeliverButton(label=localization.GetByLabel('UI/Inventory/AssetSafety/DeliverTo'))
    button.SetProgress(0.5)
    return button


@register
def create_clone_grade_button_medium():
    import eve.client.script.ui.shared.cloneGrade.button
    return eve.client.script.ui.shared.cloneGrade.button.CloneGradeButtonMedium()


@register
def create_docked_corvette_button():
    from eve.client.script.ui.shared.dockedUI import corvetteButton
    return corvetteButton.CorvetteButton()


@register
def create_docked_control_button():
    from eve.client.script.ui.shared.dockedUI import controlButton
    docked_ui_mock = mock.Mock()
    docked_ui_mock.IsExiting.return_value = False
    docked_ui_mock.InProcessOfUndocking.return_value = False
    return controlButton.Button(controller=controlButton.Controller(docked_ui_controller=docked_ui_mock, confirm_override_control=mock.MagicMock()), fixedwidth=160, fixedheight=40)


@register
def create_docked_mode_button():
    import eve.client.script.ui.shared.dockedUI.modeButton
    docked_ui_mock = mock.Mock()
    docked_ui_mock.IsExiting.return_value = False
    docked_ui_mock.InProcessOfUndocking.return_value = False
    view_state_mock = mock.Mock()
    view_state_mock.IsPrimaryViewActive.return_value = True
    return eve.client.script.ui.shared.dockedUI.modeButton.Button(controller=eve.client.script.ui.shared.dockedUI.modeButton.Controller(docked_ui_controller=docked_ui_mock, view_state_service=view_state_mock), fixedwidth=160, fixedheight=40)


@register
def create_undock_button():
    import eve.client.script.ui.shared.dockedUI.undockButton
    docked_ui_controller_mock = mock.Mock()
    docked_ui_controller_mock.IsExiting.return_value = False
    docked_ui_controller_mock.InProcessOfUndocking.return_value = False
    controller = eve.client.script.ui.shared.dockedUI.undockButton.Controller(docked_ui_controller=docked_ui_controller_mock)
    return eve.client.script.ui.shared.dockedUI.undockButton.Button(controller=controller, fixedwidth=160, fixedheight=40)


@register
def create_mutaplasmid_mutate_button():
    import eve.client.script.ui.shared.dynamicItem.craftingWindow
    controller_mock = mock.Mock()
    controller_mock.isResultPresented = False
    controller_mock.IsCraftingResultAvailable.return_value = False
    controller_mock.IsMutatorAvailable.return_value = True
    controller_mock.IsSourceItemAvailable.return_value = True
    controller_mock.IsSourceItemSelected.return_value = True
    return eve.client.script.ui.shared.dynamicItem.craftingWindow.BuildButton(fixedheight=30, fixedwidth=120, controller=controller_mock)


@register
def create_fitting_skill_requirements_button():
    from eve.client.script.ui.shared.fittingScreen import skillRequirements
    return skillRequirements.TrainNowButtonManyTypes(fixedwidth=120, fixedheight=30, skillTypesAndLvlsToUse=[])


@register
def create_industry_submit_button():
    import eve.client.script.ui.shared.industry.submitButton
    return eve.client.script.ui.shared.industry.submitButton.PrimaryButton(fixedwidth=120, fixedheight=30, label=localization.GetByLabel('UI/Industry/Start'))


@register
def create_csat_survey_button():
    import eve.client.script.ui.shared.systemMenu.csat
    return eve.client.script.ui.shared.systemMenu.csat.SurveyButton(label='Upvote', texturePath='res:/UI/Texture/classes/CSAT/up.png', iconSize=30, iconPadding=15)


@register
def create_skill_train_now_button():
    import eve.client.script.ui.shared.tooltip.itemBtns
    return eve.client.script.ui.shared.tooltip.itemBtns.TrainNowButton(typeID=11567, fixedheight=30, fixedwidth=120)


@register
def create_skill_inject_button():
    import eve.client.script.ui.shared.tooltip.itemBtns
    return eve.client.script.ui.shared.tooltip.itemBtns.InjectSkillButton(fixedheight=30, fixedwidth=120)


@register
def create_skill_buy_and_train_button():
    import eve.client.script.ui.shared.tooltip.itemBtns
    return eve.client.script.ui.shared.tooltip.skillBtns.BuyAndTrainButton(fixedheight=30, fixedwidth=120, skills=[], missingSkills=[])


@register
def create_fast_checkout_purchase_button():
    import fastcheckout.client.purchasepanels.purchaseButton
    return fastcheckout.client.purchasepanels.purchaseButton.PurchaseButton(width=110, height=29, text=localization.GetByLabel('UI/FastCheckout/Buy'), fontsize=18)


@register
def create_fast_checkout_purchase_button_small():
    import fastcheckout.client.purchasepanels.purchaseButton
    from eve.client.script.ui.control.buttons import ButtonTextBoldness
    return fastcheckout.client.purchasepanels.purchaseButton.PurchaseButton(width=16, height=16, text=localization.GetByLabel('UI/Wallet/WalletWindow/BuyPlex'), hint=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyPlex'), mouseUpTextColor=(0.0, 0.0, 0.0, 1.0), mouseEnterTextColor=(0.0, 0.0, 0.0, 1.0), mouseDownTextColor=(0.0, 0.0, 0.0, 1.0), disabledTextColor=(0.0, 0.0, 0.0, 1.0), boldText=ButtonTextBoldness.NEVER_BOLD)


@register
def create_fast_checkout_secondary_purchase_button():
    import fastcheckout.client.purchasepanels.purchaseButton
    return fastcheckout.client.purchasepanels.purchaseButton.SecondaryPurchaseButton(width=150, height=35, fontsize=14, cornerSize=20, text=localization.GetByLabel('UI/FastCheckout/SellNow'), delayedHint=localization.GetByLabel('UI/FastCheckout/SellNowButtonHint'))


@register
def create_scanner_analyze_button():
    import probescanning.analyzeButton
    scan_service_mock = mock.Mock()
    scan_service_mock.IsScanning.return_value = False
    scan_service_mock.HasAvailableProbes.return_value = True
    scan_service_mock.GetProbeData.return_value = False
    scan_service_mock.GetChargesInProbeLauncher.return_value = True
    controller_mock = probescanning.analyzeButton.AnalyzeButtonController(scan_service=scan_service_mock)
    return probescanning.analyzeButton.AnalyzeButton(controller=controller_mock, cmd=mock.Mock())


@register
def create_vgs_header_buy_plex_button():
    import eve.client.script.ui.view.aurumstore.vgsUiPrimitives
    return eve.client.script.ui.view.aurumstore.vgsUiPrimitives.HeaderBuyPlexButton(onClick=lambda *args: None)


@register
def create_vgs_header_buy_gem_button():
    import eve.client.script.ui.view.aurumstore.vgsUiPrimitives
    return eve.client.script.ui.view.aurumstore.vgsUiPrimitives.HeaderBuyGemButton(onClick=lambda *args: None)


@register
def create_vgs_detail_button():
    import eve.client.script.ui.view.aurumstore.vgsUiPrimitives
    return eve.client.script.ui.view.aurumstore.vgsUiPrimitives.DetailButton(label=localization.GetByLabel('UI/VirtualGoodsStore/ContinueShopping'), color=(0.255, 0.4, 0.545, 1.0), onClick=lambda *args: None)


@register
def create_vgs_category_button():
    import eve.client.script.ui.view.aurumstore.vgsUiPrimitives
    return eve.client.script.ui.view.aurumstore.vgsUiPrimitives.CategoryButton(width=120, height=36, label='Category', onClick=lambda *args: None)


@register
def create_vgs_sub_category_button():
    import eve.client.script.ui.view.aurumstore.vgsUiPrimitives
    return eve.client.script.ui.view.aurumstore.vgsUiPrimitives.SubCategoryButton(width=120, height=36, label='Category', onClick=lambda *args: None)


@register
def create_new_feature_button():
    import newFeatures.newFeatureNotifyButton
    return newFeatures.newFeatureNotifyButton.NewFeatureButton(text='NewFeatureButton', stretchTexturePath='res:/UI/Texture/Shared/BracketBorderWindow/button180.png', hiliteTexturePath='res:/UI/Texture/Shared/BracketBorderWindow/button180.png', height=31, width=150, fontSize=16, buttonColor=(0.8, 0.8, 0.8, 1))


@register
def create_confirm_button():
    import raffles.client.widget.confirm_button
    return raffles.client.widget.confirm_button.ConfirmButton(label='Buy', on_click=lambda : None)


@register
def create_quick_buy_button():
    import raffles.client.widget.quick_buy_button
    raffle_mock = mock.Mock()
    raffle_mock.is_ticket_owner = True
    raffle_mock.tickets_owned_count = 7
    raffle_mock.is_finished = False
    raffle_mock.is_sold_out = False
    raffle_mock.winner_id = None
    raffle_mock.is_winner_unseen = False
    raffle_mock.is_expired = False
    raffle_mock.ticket_price = 100
    return raffles.client.widget.quick_buy_button.QuickBuyButton(raffle=raffle_mock)


@register
def create_filament_random_jump_button():
    import randomJump.client.RandomJumpButton
    controller_mock = mock.Mock()
    controller_mock.isReady = True
    controller_mock.isActivating = False
    controller_mock.isFinished = False
    controller_mock.errors = []
    controller_mock.GetText = lambda : localization.GetByLabel('UI/Abyss/Activate')
    return randomJump.client.RandomJumpButton.RandomJumpButton(controller=controller_mock, fixedheight=30)


@register
def create_pvp_filament_jump_button():
    from pvpFilaments.client.activation_window import pvpFilamentJumpButton
    controller_mock = mock.Mock()
    controller_mock.isReady = True
    controller_mock.isActivating = False
    controller_mock.isFinished = False
    controller_mock.errors = []
    controller_mock.displayed_errors = []
    controller_mock.GetText = lambda : localization.GetByLabel('UI/Abyss/Activate')
    return pvpFilamentJumpButton.PVPFilamentJumpButton(controller=controller_mock, fixedheight=28)


@register
def create_vgs_button_core():
    import eve.client.script.ui.shared.vgs.buttonCore
    return eve.client.script.ui.shared.vgs.buttonCore.ButtonCore(text='VGS ButtonCore')


@register
def create_vgs_buy_button():
    import eve.client.script.ui.shared.vgs.button
    return eve.client.script.ui.shared.vgs.button.VgsBuyButton(text='Buy')


@register
def create_vgs_():
    import eve.client.script.ui.shared.vgs.button
    return eve.client.script.ui.shared.vgs.button.BuyButtonIsk(state=uiconst.UI_NORMAL)


@register
def create_multi_training_buy_button_isk():
    from eve.client.script.ui.shared.monetization import multiTrainingOverlay
    return multiTrainingOverlay.MultiTrainingBuyButtonIsk()


@register
def create_vgs_buy_button_isk_small():
    import eve.client.script.ui.shared.vgs.button
    return eve.client.script.ui.shared.vgs.button.BuyButtonIskSmall(state=uiconst.UI_NORMAL)


@register
def create_skin_license_buy_button_isk():
    import eve.client.script.ui.shared.skins.buyButton
    return eve.client.script.ui.shared.skins.buyButton.SkinLicenseBuyButtonIsk(state=uiconst.UI_NORMAL)


@register
def create_skin_material_buy_button_isk():
    import eve.client.script.ui.shared.skins.buyButton
    return eve.client.script.ui.shared.skins.buyButton.SkinMaterialBuyButtonIsk(state=uiconst.UI_NORMAL)


@register
def create_vgs_buy_button_plex():
    import eve.client.script.ui.shared.vgs.buyButtonPlex
    return eve.client.script.ui.shared.vgs.buyButtonPlex.BuyButtonPlex()


@register
def create_vgs_buy_button_aur():
    import eve.client.script.ui.shared.vgs.button
    return eve.client.script.ui.shared.vgs.button.BuyButtonAur(state=uiconst.UI_NORMAL)


@register
def create_multi_training_buy_button_aur():
    from eve.client.script.ui.shared.monetization import multiTrainingOverlay
    return multiTrainingOverlay.MultiTrainingBuyButtonAur(state=uiconst.UI_NORMAL)


@register
def create_vgs_buy_button_aur_small():
    import eve.client.script.ui.shared.vgs.button
    return eve.client.script.ui.shared.vgs.button.BuyButtonAurSmall(state=uiconst.UI_NORMAL)


@register
def create_skin_license_buy_button_aur():
    import eve.client.script.ui.shared.skins.buyButton
    return eve.client.script.ui.shared.skins.buyButton.SkinLicenseBuyButtonAur(state=uiconst.UI_NORMAL)


@register
def create_skin_material_buy_button_aur():
    import eve.client.script.ui.shared.skins.buyButton
    return eve.client.script.ui.shared.skins.buyButton.SkinMaterialBuyButtonAur(state=uiconst.UI_NORMAL)


@register
def create_skill_extract_button():
    import eve.client.script.ui.skilltrading.skillExtractorWindow
    return eve.client.script.ui.skilltrading.skillExtractorWindow.ExtractButton(width=250, height=32, controller=mock.Mock())


@register
def create_add_access_list_group_button():
    from eve.client.script.ui.structure.accessGroups.addCont import AddGroupCont
    return AddGroupCont(align=uiconst.TOPLEFT, width=260, controller=None)


@register
def create_resource_wars_objective_action_button():
    import resourcewars.client.objectivefeedback
    return resourcewars.client.objectivefeedback.ActionButton(width=120, height=30, text='ActionButton', fontsize=12, onMouseEventFunc=lambda x: None)


@register
def create_resource_wars_rewards_action_button():
    import resourcewars.client.rewardsfeedback
    return resourcewars.client.rewardsfeedback.ActionButton(width=120, height=30, text='ActionButton', fontsize=12)


@register
def create_raffles_sort_direction_button():
    import raffles.client.history.filter
    return raffles.client.history.filter.SortDirectionButton(texture_path='res:/UI/Texture/classes/HyperNet/sort_descending.png')


@register
def create_raffles_save_filter_button():
    import raffles.client.widget.saved_filter_combo
    controller_mock = mock.Mock()
    controller_mock.bind = lambda **kwargs: None
    controller_mock.is_filter_default = False
    return raffles.client.widget.saved_filter_combo.SaveFilterButton(controller=controller_mock)


@register
def create_industry_activity_toggle_button():
    from eve.client.script.ui.shared.industry import activitySelectionButtons
    return activitySelectionButtons.ActivityToggleButtonGroupButton(width=32, height=32, iconPath='res:/UI/Texture/classes/Industry/activity/manufacturing.png', iconSize=26, activityID=1, colorSelected=(1.0, 0.6, 0.0, 1.0), controller=mock.Mock())


@register
def create_bookmark_add_button():
    from eve.client.script.ui.shared.agencyNew.ui import bookmarksBar
    return bookmarksBar.AddBookmarkButton(height=32)


@register
def create_sov_capital_button():
    import sovDashboard.claimedSystems
    return sovDashboard.claimedSystems.CapitalButton()


@register
def create_fitting_util_button():
    from eve.client.script.ui.shared.fitting import utilBtns
    button_data = utilBtns.UtilBtnData(hint=localization.GetByLabel('UI/Fitting/RemoveCharge'), iconPath='ui_38_16_200', func=lambda : None, isActive=True, onlineBtn=1)
    button = utilBtns.FittingUtilBtn(icon=button_data.iconPath, btnData=button_data, opacity=1.0)
    button.SetBtnColorBasedOnIsActive()
    return button


@register
def create_info_panel_list_surroundings_button():
    from eve.client.script.ui.shared.infoPanels import infoPanelLocationInfo
    import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
    button = eve.client.script.ui.shared.infoPanels.listSurroundingsBtn.ListSurroundingsBtn(width=24, height=24, texturePath='res:/UI/Texture/Classes/InfoPanels/LocationInfo.png', iconSize=16, showIcon=True, useDynamicMapItems=True, uniqueUiName=pConst.UNIQUE_NAME_LOCATION_ITEMS)
    button.hint = localization.GetByLabel('UI/Neocom/ListItemsInSystem')
    button.sr.groupByType = 1
    button.filterCurrent = 1
    button.SetSolarsystemID(session.solarsystemid2)
    return button


@register
def create_fitting_filter_button():
    from eve.client.script.ui.shared.fittingScreen import filterBtn
    return filterBtn.FilterBtn(width=30, height=30, texturePath='res:/UI/Texture/classes/Fitting/filterIconHighSlot.png', buttonType=filterBtn.BTN_TYPE_HISLOT, iconSize=30, isChecked=False, hintLabelPath=localization.GetByLabel('UI/Fitting/FittingWindow/FilterHiSlot'), args=())


@register
def create_structure_service_toggle_button():
    from eve.client.script.ui.structure.structureSettings import serviceListCont
    return serviceListCont.ServiceToggleButton(controller=mock.Mock(), iconPath='res:/UI/Texture/classes/ProfileSettings/defense.png', hint=localization.GetByLabel('UI/StructureSettings/ServiceDefense'))


@register
def create_map_view_settings_button():
    from eve.client.script.ui.shared.mapView import mapViewConst
    from eve.client.script.ui.shared.mapView.controls import mapViewSettingButton
    return mapViewSettingButton.MapViewSettingButton(mapViewID=mapViewConst.MAPVIEW_PRIMARY_ID, settingGroupKey=mapViewConst.VIEWMODE_LAYOUT_SETTINGS, texturePath='res:/UI/Texture/Icons/44_32_4.png')


@register
def create_dockable_panel_header_button():
    import eve.client.script.ui.shared.mapView.dockPanel
    return eve.client.script.ui.shared.mapView.dockPanel.DockablePanelHeaderButton(hint=localization.GetByLabel('/Carbon/UI/Controls/Window/Minimize'), texturePath='res:/UI/Texture/classes/DockPanel/minimizeButton.png')


@register
def create_industry_activity_button():
    import eve.client.script.ui.shared.industry.blueprintEntry
    return eve.client.script.ui.shared.industry.blueprintEntry.ActivityButtonIcon(width=24, height=24, iconSize=20, texturePath='res:/UI/Texture/classes/Industry/manufacturing.png', hint=localization.GetByLabel('UI/Industry/ActivityNotAvailable'), isHoverBGUsed=True, colorSelected=(1.0, 0.6, 0.0, 1.0), args=(None, None))


@register
def create_info_panel_icon_button():
    import utillib
    from eve.client.script.ui.shared.infoPanels import infoPanelContainer
    from eve.client.script.ui.shared.infoPanels.infoPanelLocationInfo import InfoPanelLocationInfo
    controller = utillib.KeyVal(settingsID='BUTTON_BAZAAR', OnButtonDragStart=lambda _: None, OnButtonDragEnd=lambda _: None)
    return infoPanelContainer.ButtonIconInfoPanel(controller=controller, infoPanelCls=InfoPanelLocationInfo, texturePath='res:/UI/Texture/Classes/InfoPanels/Route.png')


@register
def create_fitting_radio_button():
    from eve.client.script.ui.shared.fittingScreen.fittingPanels import chargeButtons
    return chargeButtons.ModuleChargeRadioButton(moduleTypeID=566, controller=mock.Mock())


@register
def create_fitting_simulation_button():
    from eve.client.script.ui.shared.fittingScreen import shipFittingSimulationButton
    return shipFittingSimulationButton.ShipFittingSimulationButton(width=24, height=24, iconSize=24, hint=localization.GetByLabel('UI/Fitting/FittingWindow/SimulateShip'))


@register
def create_character_select_delete_button():
    import eve.client.script.ui.login.charSelection.characterSlots
    return eve.client.script.ui.login.charSelection.characterSlots.DeleteButton(height=14, texturePath='res:/UI/Texture/Icons/Plus_Small.png', state=uiconst.UI_NORMAL, color=(1.0, 0.0, 0.0, 1.0), hint=localization.GetByLabel('UI/CharacterSelection/CompleteTermination'), rotation=math.pi / 4.0)


@register
def create_cc_hex_button():
    import eve.client.script.ui.login.charcreation_new.hexes
    return eve.client.script.ui.login.charcreation_new.hexes.CCHexButtonRandomize(state=uiconst.UI_NORMAL, width=64, height=64, pickRadius=32, iconNum=0, hexName=localization.GetByLabel('UI/CharacterCreation/RandomizeDollTooltip'))


@register
def create_inflight_safety_button():
    import eve.client.script.ui.inflight.shipSafetyButton
    return eve.client.script.ui.inflight.shipSafetyButton.SafetyButton()


@register
def create_inflight_stance_button():
    import eve.client.script.ui.inflight.shipstance
    from eve.client.script.ui.inflight import shipstance
    ship_id = session.shipid
    type_id = 34828
    kwargs = shipstance.get_ship_stance_buttons_args(type_id, ship_id)[0]
    return eve.client.script.ui.inflight.shipstance.ShipStanceButton(shipID=ship_id, typeID=type_id, width=36, height=36, **kwargs)


@register
def create_inflight_fighter_drag_button():
    import eve.client.script.ui.inflight.squadrons.squadronsUI
    return eve.client.script.ui.inflight.squadrons.squadronsUI.FighterDragButton(iconSize=24, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/positionFighters_Up.png')


@register
def create_inflight_fighters_open_bay_button():
    import eve.client.script.ui.inflight.squadrons.squadronsUI
    return eve.client.script.ui.inflight.squadrons.squadronsUI.FightersButtonOpenBay()


@register
def create_cc_arrow_tech_button():
    from eve.client.script.ui.login.charcreation import technologyViewUtils
    return technologyViewUtils.ArrowTechButton(width=technologyViewUtils.GetTechNavArrowSize(), height=technologyViewUtils.GetTechNavArrowSize(), iconTexture=technologyViewUtils.ARROW_TEXTURE, iconSize=technologyViewUtils.GetTechNavArrowIconSize(), rotation=math.pi)


@register
def create_ship_hud_group_all_button():
    import eve.client.script.ui.inflight.shipHud.groupAllIcon
    button = eve.client.script.ui.inflight.shipHud.groupAllIcon.GroupAllButton()
    button.groupAllIcon.state = uiconst.UI_NORMAL
    button.groupAllIcon.SetTexturePath(button.groupAllITexturePath)
    return button


@register
def create_ship_hud_autopilot_button():
    from eve.client.script.ui.inflight.shipHud import leftSideButton
    return leftSideButton.LeftSideButtonAutopilot()


@register
def create_ship_hud_scanner_button():
    from eve.client.script.ui.inflight.shipHud import leftSideButton
    return leftSideButton.LeftSideButtonScanner()


@register
def create_ship_hud_cargo_button():
    from eve.client.script.ui.inflight.shipHud.leftSideButtons import leftSideButtonCargo
    return leftSideButtonCargo.LeftSideButtonCargo()


@register
def create_ship_hud_moon_mining_scheduler_button():
    from eve.client.script.ui.moonmining import moonminingExtraHudBtns
    return moonminingExtraHudBtns.SchedulerHudBtn()


@register
def create_ship_hud_max_speed_button():
    from eve.client.script.ui.inflight.shipHud import shipUI
    return shipUI.MaxSpeedButton(controller=mock.Mock())


@register
def create_ship_hud_stop_button():
    from eve.client.script.ui.inflight.shipHud import shipUI
    return shipUI.StopButton(controller=mock.Mock())


@register
def create_ship_hud_buff_button():
    import eve.client.script.ui.inflight.shipHud.buffButtons
    from eve.common.script.mgt import buffBarConst
    jamming_type, graphic_id = buffBarConst.BUFF_SLOT_ICONS.items()[0]
    return eve.client.script.ui.inflight.shipHud.buffButtons.OffensiveBuffButton(width=40, height=40, graphicID=graphic_id, effectType=jamming_type)


@register
def create_system_wide_effect_button():
    from eve.client.script.ui.inflight.shipHud import systemWideEffectButton
    from eve.client.script.ui.inflight.shipHud.buffButtons import ICON_SIZE
    return systemWideEffectButton.SystemWideEffectButton(width=ICON_SIZE, height=ICON_SIZE, sourceTypeID=57044)


@register
def create_ship_module_button():
    from eve.client.script.ui.inflight.shipHud.shipSlot import ShipSlot
    from eve.client.script.ui.inflight.shipModuleButton import shipmodulebutton
    from utillib import KeyVal
    slot = ShipSlot(width=64, height=64)
    module_button = shipmodulebutton.ModuleButton(parent=slot)
    module_info = KeyVal(typeID=566, itemID=session.shipid, flagID=const.flagHiSlot0, effects={})
    module_info[const.ixSingleton] = False
    module_button.Setup(module_info)
    return slot


@register
def create_ship_hud_extra_button():
    from eve.client.script.ui.inflight.shipModuleButton import extraBtnShipSlot
    button = extraBtnShipSlot.ExtraBtnShipSlot()
    button.SetButtonIcon('res:/UI/Texture/classes/Moonmining/iconReady.png')
    return button


@register
def create_ship_hud_overload_button():
    import eve.client.script.ui.inflight.shipHud.overloadBtn
    return eve.client.script.ui.inflight.shipHud.overloadBtn.OverloadBtn(fitKey='Hi', powerEffectID=const.effectHiPower, activationID=None)


@register
def create_ship_hud_release_structure_control_button():
    import eve.client.script.ui.inflight.shipHud.releaseControlBtn
    return eve.client.script.ui.inflight.shipHud.releaseControlBtn.ReleaseControlBtn(structureTypeID=35832)


@register
def create_show_market_details_button():
    from eve.client.script.ui.control.utilButtons import marketDetailsButton
    return marketDetailsButton.ShowMarketDetailsButton(typeID=4050)


@register
def create_show_info_button():
    from eve.client.script.ui.control.utilButtons import showInfoButton
    return showInfoButton.ShowInfoButton(typeID=670)


@register
def create_show_in_map_button():
    from eve.client.script.ui.control.utilButtons import showInMapButton
    return showInMapButton.ShowInMapButton(itemID=30003803)


@register
def create_project_discovery_color_filter_button():
    from projectdiscovery.client.projects.exoplanets.ui import colorfilterbutton
    return colorfilterbutton.ColorFilterButton()


@register
def create_ship_tree_info_panel_button():
    import eve.client.script.ui.shared.infoPanels.infoPanelShipTree
    return eve.client.script.ui.shared.infoPanels.infoPanelShipTree.ShipTreeButtonIcon(width=53, height=53, iconSize=32, isHoverBGUsed=True, texturePath='res:/ui/texture/icons/19_128_1.png')


@register
def create_info_panel_expand_button():
    import eve.client.script.ui.shared.infoPanels.InfoPanelBase
    return eve.client.script.ui.shared.infoPanels.InfoPanelBase.ExpandButton(width=24, height=24, expanded=False)


@register
def create_market_ticker_toggle():
    import eve.client.script.ui.shared.market.ticker
    return eve.client.script.ui.shared.market.ticker.TickerToggleButton(controller=mock.Mock())


@register
def create_character_sheet_icon_button_cont():
    from carbonui.primitives.sprite import Sprite
    from eve.client.script.ui.shared.neocom.charsheet.characterOverviewPanel import characterOverviewElements
    icon_button_cont = characterOverviewElements.IconButtonCont(width=50, height=50)
    Sprite(parent=icon_button_cont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Race/Gallente.png', iconSize=50)
    return icon_button_cont


@register
def create_standings_action_button():
    from eve.client.script.ui.shared.neocom.charsheet.standingsPanel import standingsHeaderButtons
    return standingsHeaderButtons.StandingActionButton(state=uiconst.UI_NORMAL, width=26, height=26, texturePath='res:/UI/Texture/Classes/Standings/Actions/completeMission.png', actionID=10, standingData=mock.Mock())


@register
def create_standings_benefit_button():
    from eve.client.script.ui.shared.neocom.charsheet.standingsPanel import standingsHeaderButtons
    return standingsHeaderButtons.StandingBenefitButton(state=uiconst.UI_NORMAL, width=26, height=26, texturePath='res:/UI/Texture/Classes/Standings/Benefits/reprocessingTax.png', benefitID=1, standingData=mock.Mock())


@register
def create_neocom_eve_menu_button():
    import eve.client.script.ui.shared.neocom.neocom.buttons.buttonEveMenu
    button_data_mock = mock.Mock()
    button_data_mock.isBlinking = False
    return eve.client.script.ui.shared.neocom.neocom.buttons.buttonEveMenu.ButtonEveMenu(state=uiconst.UI_NORMAL, width=36, height=36, btnData=button_data_mock)


@register
def create_neocom_overflow_button():
    import eve.client.script.ui.shared.neocom.neocom.buttons.overflowButton
    return eve.client.script.ui.shared.neocom.neocom.buttons.overflowButton.OverflowButton(state=uiconst.UI_NORMAL, width=36, height=16)


@register
def create_planet_icon_button():
    import eve.client.script.ui.shared.planet.pinContainers.BasePinContainer
    return eve.client.script.ui.shared.planet.pinContainers.BasePinContainer.IconButton(width=25, height=25, size=25, typeID=2288)


@register
def create_preview_side_panel_button():
    import eve.client.script.ui.shared.preview
    return eve.client.script.ui.shared.preview.SidePanelButton()


@register
def create_redeem_button():
    from eve.client.script.ui.shared.redeem import newRedeemPanel
    return newRedeemPanel.RedeemButton(state=uiconst.UI_NORMAL, width=1024, height=newRedeemPanel.REDEEM_BUTTON_HEIGHT, borderColor=newRedeemPanel.REDEEM_BUTTON_BORDER_COLOR, backgroundColor=newRedeemPanel.REDEEM_BUTTON_BACKGROUND_COLOR, fillColor=newRedeemPanel.REDEEM_BUTTON_FILL_COLOR, textColor=newRedeemPanel.TEXT_COLOR, animationDuration=newRedeemPanel.DEFAULT_ANIMATION_DURATION, controller=mock.Mock())


@register
def create_vgs_header_button():
    import eve.client.script.ui.shared.vgs.headerButton
    return eve.client.script.ui.shared.vgs.headerButton.HeaderButton(texturePath='res:/UI/Texture/Vgs/exit.png', hint=localization.GetByLabel('UI/Common/Buttons/Close'), onClick=lambda : None)


@register
def create_vgs_collapse_button():
    import eve.client.script.ui.view.aurumstore.vgsOffer
    return eve.client.script.ui.view.aurumstore.vgsOffer.CollapseButton()


@register
def create_vgs_character_button():
    import eve.client.script.ui.view.aurumstore.vgsOffer
    return eve.client.script.ui.view.aurumstore.vgsOffer.CharacterButton(width=38, height=38, charID=session.charid, onClick=lambda *args: None)


@register
def create_vgs_filter_button():
    import eve.client.script.ui.view.aurumstore.vgsOfferFilterBar
    return eve.client.script.ui.view.aurumstore.vgsOfferFilterBar.FilterButton(height=32, label='Tag name', onClick=lambda *args: None)


@register
def create_vgs_exit_button():
    import eve.client.script.ui.view.aurumstore.vgsUiPrimitives
    return eve.client.script.ui.view.aurumstore.vgsUiPrimitives.ExitButton(onClick=lambda : None)


@register
def create_sensor_suite_site_button():
    import sensorsuite.overlay.siteconst
    import sensorsuite.overlay.sitefilter
    from utillib import KeyVal
    return sensorsuite.overlay.sitefilter.SiteButton(filterConfig=KeyVal(siteIconData=KeyVal(icon='res:/UI/Texture/Icons/38_16_150.png', outerTextures=('res:/UI/Texture/classes/SensorSuite/bracket_bookmark_1.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_2.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_3.png', 'res:/UI/Texture/classes/SensorSuite/bracket_bookmark_4.png'), color=sensorsuite.overlay.siteconst.SITE_COLOR_BOOKMARK), label='UI/Inflight/Scanner/SharedSiteFilterLabel'))


@register
def create_wallet_buy_plex_button():
    import eve.client.script.ui.shared.neocom.wallet.buyPlexButton
    return eve.client.script.ui.shared.neocom.wallet.buyPlexButton.BuyPlexButton()


@register
def create_fitting_side_panel_button():
    import eve.client.script.ui.shared.fittingScreen.sidePanelButtons
    return eve.client.script.ui.shared.fittingScreen.sidePanelButtons.SidePanelButton(width=45, height=40, tabText=localization.GetByLabel('UI/Fitting/FittingWindow/Skins'), texturePath='res:/UI/Texture/classes/Fitting/tabSkins.png', iconSize=40, isLeftAlign=True, controller=mock.Mock())


@register
def create_x_button():
    import drawingpolygon.xbutton
    return drawingpolygon.xbutton.XButton(button_function=lambda : None)


@register
def create_project_discovery_x_button():
    from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import xbutton
    return xbutton.XButton(mouse_enter_callback=lambda **kwargs: None)


@register
def create_cc_back_button():
    from eve.client.script.ui.login.charcreation.empireui import backButton
    from eve.client.script.ui.login.charcreation.steps import bloodLineStep
    from eve.common.lib import appConst
    return backButton.BackButton(width=bloodLineStep.BACK_BUTTON_WIDTH * bloodLineStep.ccScalingUtils.GetScaleFactor(), height=bloodLineStep.BACK_BUTTON_HEIGHT * bloodLineStep.ccScalingUtils.GetScaleFactor(), raceID=appConst.raceCaldari, iconSize=bloodLineStep.TECH_NAV_ARROW_SIZE * bloodLineStep.ccScalingUtils.GetScaleFactor())


@register
def create_vgs_logo_home_button():
    import eve.client.script.ui.view.aurumstore.vgsUiPrimitives
    return eve.client.script.ui.view.aurumstore.vgsUiPrimitives.LogoHomeButton(onClick=lambda : None)


@register
def create_character_select_open_store_button():
    import eve.client.script.ui.login.charSelection.characterSelection
    return eve.client.script.ui.login.charSelection.characterSelection.OpenStoreButton()


@register
def create_vgs_redeeming_queue_button():
    import eve.client.script.ui.view.aurumstore.vgsUiPrimitives
    return eve.client.script.ui.view.aurumstore.vgsUiPrimitives.RedeemingQueueButton(height=32)


@register
def create_clone_grade_upgrade_button():
    import eve.client.script.ui.shared.cloneGrade.upgradeButton
    return eve.client.script.ui.shared.cloneGrade.upgradeButton.UpgradeButton(width=350, height=41, text=localization.GetByLabel('UI/CloneState/UpgradeToOmega'))


@register
def create_login_rewards_header_toggle_button():
    from utillib import KeyVal
    from eve.client.script.ui.shared.loginRewards import rewardToggleButtonGroupButton
    return rewardToggleButtonGroupButton.RewardToggleButtonGroupButtonHeader(width=300, height=120, controller=mock.Mock(), label=localization.GetByLabel('UI/LoginRewards/RewardHeaderDefault'), subLabel=localization.GetByLabel('UI/LoginRewards/CollectText'), texturePath='res:/UI/Texture/classes/LoginCampaign/backgrounds/default.png', textureInfo=KeyVal(texturePath='res:/UI/Texture/classes/LoginCampaign/backgrounds/default.png', textureWidth=1068, textureHeight=614, textureOpacity=1.0, textureOffset=0, textureAlign=uiconst.TOPLEFT))


@register
def create_empire_selection_button():
    from eve.common.lib import appConst
    from eve.client.script.ui.login.charcreation_new.steps.empireSelection import empireSelectionButton
    return empireSelectionButton.EmpireSelectionButton(width=120, height=120, maxWidth=32, factionID=appConst.factionGallenteFederation)


@register
def create_cc_empire_themed_button():
    from eve.client.script.ui.login.charcreation.empireui import empireThemedButtons
    from eve.common.lib import appConst
    return empireThemedButtons.EmpireThemedButton(label=localization.GetByLabel('UI/CharacterCreation/CustomizeAppearance').upper(), raceID=appConst.raceCaldari, width=551, height=46, padding=(118, 0, 118, 0), buttonState=empireThemedButtons.EmpireThemedButtonState.NORMAL, mouseOverSound='ui_es_mouse_over_customize_appearance_play', mouseExitSound='ui_es_mouse_over_customize_appearance_stop')
