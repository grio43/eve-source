#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\combatLogMessages.py


def SendCombatLogAmountMessage(dogmaLM, recipientID, objectID, messageID, moduleTypeID, amount):
    messageArgs = {'amount': amount,
     'specialObject': objectID,
     'type': moduleTypeID}
    dogmaLM.SendMessage(recipientID, ('OnCombatMessage', messageID, messageArgs))
