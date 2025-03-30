#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\radialMenuScanner.py
from eve.client.script.ui.inflight.radialMenuShipUI import RadialMenuShipUI
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction, RadialMenuOptionsInfo
from carbonui.uicore import uicore

class RadialMenuScanner(RadialMenuShipUI):

    def ApplyAttributes(self, attributes):
        RadialMenuShipUI.ApplyAttributes(self, attributes)

    def GetMyActions(self, *args):
        iconOffset = 1
        allWantedMenuOptions = []
        allWantedMenuOptions.append(SimpleRadialMenuAction(option1='UI/Inflight/Scanner/MoonAnalysis', func=uicore.cmd.GetCommandToExecute('OpenMoonScan'), iconPath='res:/UI/Texture/Icons/moonscan.png', iconOffset=iconOffset, commandName='OpenMoonScan'))
        allWantedMenuOptions.extend([SimpleRadialMenuAction(option1='UI/Inflight/Scanner/DirectionalScanner', func=uicore.cmd.GetCommandToExecute('OpenDirectionalScanner'), iconPath='res:/UI/Texture/Icons/d-scan.png', iconOffset=iconOffset, commandName='OpenDirectionalScanner'), SimpleRadialMenuAction(option1='UI/Map/MapPallet/btnSolarsystemMap', func=uicore.cmd.GetCommandToExecute('CmdToggleSolarSystemMap'), iconPath='res:/UI/Texture/classes/ProbeScanner/solarsystemMapButton.png', iconOffset=iconOffset, commandName='CmdToggleSolarSystemMap'), SimpleRadialMenuAction(option1='UI/Inflight/Scanner/ProbeScanner', func=uicore.cmd.GetCommandToExecute('ToggleProbeScanner'), iconPath='res:/UI/Texture/Icons/probe_scan.png', iconOffset=iconOffset, commandName='ToggleProbeScanner')])
        activeSingleOptions = {menuAction.option1Path:menuAction for menuAction in allWantedMenuOptions if menuAction.option1Path}
        optionsInfo = RadialMenuOptionsInfo(allWantedMenuOptions=allWantedMenuOptions, activeSingleOptions=activeSingleOptions)
        return optionsInfo
