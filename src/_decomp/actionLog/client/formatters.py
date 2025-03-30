#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\actionLog\client\formatters.py
import localization
STRONG_COLOR = '<color=0xff00ffff>'
FAINT_COLOR = '<color=0x77ffffff>'
NORMAL_COLOR = '<color=0xffffffff>'
BOUNTY_PAYOUT_COLOR = '<color=0xff00aa00>'
MINING_AMOUNT_COLOR = '<color=0xffaaaa00>'
MINING_AMOUNT_STRONG_COLOR = '<color=0xffdddd1c>'
PIRATE_KILLED_HIGHLIGHTED_COLOR = '<color=0xffdddd1c>'
PIRATE_KILLED_NORMAL_COLOR = '<color=0xffaaaa00>'

def FormatBountyMessage(normalFontSize, bounty):
    return localization.GetByLabel('UI/Inflight/ActivityLog/BountyAddedToPayoutMessage1', normalFont=_GetFontSizeString(normalFontSize), bountyPayoutColor=BOUNTY_PAYOUT_COLOR, bounty=bounty, faintColor=FAINT_COLOR)


def FormatModifiedBountyMessage(normalFontSize, bounty):
    return localization.GetByLabel('UI/Inflight/ActivityLog/ModifiedBountyAddedToPayoutMessage1', normalFont=_GetFontSizeString(normalFontSize), bountyPayoutColor=BOUNTY_PAYOUT_COLOR, bounty=bounty, faintColor=FAINT_COLOR)


def FormatMiningMessage(normalFontSize, oreTypeID, amount, amountWasted):
    return localization.GetByLabel('UI/Inflight/ActivityLog/MinedMessage1', faintColor=FAINT_COLOR, normalFont=_GetFontSizeString(normalFontSize), smallFont=_GetFontSizeString(normalFontSize - 2), amountMinedColor=MINING_AMOUNT_COLOR, amount=amount, normalColor=NORMAL_COLOR, oreTypeID=oreTypeID, amountWasted=amountWasted)


def FormatMiningRewardsMessage(normalFontSize, oreTypeID, amount):
    return localization.GetByLabel('UI/Inflight/ActivityLog/VariableRewardMined', normalFont=_GetFontSizeString(normalFontSize), smallFont=_GetFontSizeString(normalFontSize - 2), textColor=MINING_AMOUNT_COLOR, highlightedTextColor=MINING_AMOUNT_STRONG_COLOR, amount=amount, oreTypeID=oreTypeID)


def FormatOreDepositedMessage(normalFontSize, oreTypeID, amount, charID):
    return localization.GetByLabel('UI/Inflight/ActivityLog/OreDeposited', charID=charID, normalFont=_GetFontSizeString(normalFontSize), smallFont=_GetFontSizeString(normalFontSize - 2), textColor=MINING_AMOUNT_COLOR, highlightedTextColor=MINING_AMOUNT_STRONG_COLOR, amount=amount, oreTypeID=oreTypeID)


def FormatPirateKilledMessage(normalFontSize, killerName, killedName):
    return localization.GetByLabel('UI/Inflight/ActivityLog/PirateKilled', killerName=killerName, normalFont=_GetFontSizeString(normalFontSize), smallFont=_GetFontSizeString(normalFontSize - 2), highlightedTextColor=PIRATE_KILLED_HIGHLIGHTED_COLOR, textColor=PIRATE_KILLED_NORMAL_COLOR, killedName=killedName)


def _GetFontSizeString(fontSize):
    normalFont = '<font size=%s>' % str(fontSize)
    return normalFont
