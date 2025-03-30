#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\imageserver\validate_package.py
import sys
import argparse
import os
import logging
import time
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
pkgspath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if pkgspath not in sys.path:
    sys.path.append(pkgspath)
mainlinepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if mainlinepath not in sys.path:
    sys.path.append(mainlinepath)
from utils import ReadMapping, WriteMapping
from confluence.confluence import Confluence
from validate.mappingchange import MappingChangeType, MappingChange
import platformtools.compatibility.exposure.artpipeline.tools.utils.texturediff as TextureDiff
_sender = 'evegraphicsreport=ccpgames.com@mg.tech.ccp.is'
recipients = os.getenv('MAIL_RECIPIENTS_LIST', None)
_mailRecipients = []
if recipients is not None:
    _mailRecipients = [ r.strip() for r in recipients.split(',') ]
_confluenceSpaceKey = 'TTL'
_confluenceRootPage = 'IconReports'
_maxTexelTolerance = 2
_rmsTolerance = 2.0

def AddMappingChange(existingMappingChanges, mappingName, type, id, oldFolder = None, oldValue = None, newFolder = None, newValue = None, iconType = None, diffData = None):
    for change in existingMappingChanges:
        if change.Matches(type, oldFolder, oldValue, newFolder, newValue, iconType):
            change.AddId(id)
            return

    existingMappingChanges.append(MappingChange(mappingName, type, id, oldFolder, oldValue, newFolder, newValue, iconType, diffData))


def CompareMappings(mappingName, oldFolder, oldMapping, newFolder, newMapping, filter = None):
    results = []

    def _Filter(map):
        if not filter:
            return map
        else:
            newDict = {}
            for key, val in map.iteritems():
                if isinstance(val, dict):
                    newVal = {}
                    for type, path in val.iteritems():
                        if filter in path.lower():
                            newVal[type] = path

                    if len(newVal) > 0:
                        newDict[key] = newVal
                elif filter in val.lower():
                    newDict[key] = val

            return newDict

    filteredOldMapping = _Filter(oldMapping)
    filteredNewMapping = _Filter(newMapping)
    oldMappingSet = set(filteredOldMapping.keys())
    newMappingSet = set(filteredNewMapping.keys())
    for each in newMappingSet.difference(oldMappingSet):
        newEntry = filteredNewMapping[each]
        if isinstance(newEntry, dict):
            for e, value in newEntry.iteritems():
                AddMappingChange(results, mappingName, MappingChangeType.ENTRY_ADDED, each, iconType=e, newFolder=newFolder, newValue=value)

        else:
            AddMappingChange(results, mappingName, MappingChangeType.ENTRY_ADDED, each, newFolder=newFolder, newValue=newEntry)

    for each in oldMappingSet.difference(newMappingSet):
        oldEntry = filteredOldMapping[each]
        if isinstance(oldEntry, dict):
            for e, value in oldEntry.iteritems():
                AddMappingChange(results, mappingName, MappingChangeType.ENTRY_DELETED, each, iconType=e, oldFolder=oldFolder, oldValue=value)

        else:
            AddMappingChange(results, mappingName, MappingChangeType.ENTRY_DELETED, each, oldFolder=oldFolder, oldValue=oldEntry)

    for each in newMappingSet.intersection(oldMappingSet):
        oldEntry = filteredOldMapping[each]
        newEntry = filteredNewMapping[each]
        if isinstance(oldEntry, dict) and isinstance(newEntry, dict):
            oldEntrySet = set(oldEntry.keys())
            newEntrySet = set(newEntry.keys())
            for e in newEntrySet.difference(oldEntrySet):
                AddMappingChange(results, mappingName, MappingChangeType.ICON_TYPE_ADDED, each, iconType=e, newFolder=newFolder, newValue=newEntry[e])

            for e in oldEntrySet.difference(newEntrySet):
                AddMappingChange(results, mappingName, MappingChangeType.ICON_TYPE_DELETED, each, iconType=e, oldFolder=oldFolder, oldValue=oldEntry[e])

            for e in newEntrySet.intersection(oldEntrySet):
                oldIconPath = oldEntry[e]
                newIconPath = newEntry[e]
                if oldIconPath != newIconPath:
                    AddMappingChange(results, mappingName, MappingChangeType.ICON_NAME_CHANGED, each, iconType=e, oldFolder=oldFolder, oldValue=oldEntry[e], newFolder=newFolder, newValue=newEntry[e])
                else:
                    diff = TextureDiff.TextureDiff(os.path.join(oldFolder, oldIconPath), 'old', os.path.join(newFolder, newIconPath), 'new', maxTexelTolerance=_maxTexelTolerance, rmsTolerance=_rmsTolerance)
                    if diff.IsDifferent():
                        AddMappingChange(results, mappingName, MappingChangeType.ICON_CHANGED, each, iconType=e, oldFolder=oldFolder, oldValue=oldIconPath, newFolder=newFolder, newValue=newIconPath, diffData=diff)

        elif oldEntry != newEntry:
            AddMappingChange(results, mappingName, MappingChangeType.ICON_NAME_CHANGED, each, oldFolder=oldFolder, oldValue=oldEntry, newFolder=newFolder, newValue=newEntry)
        else:
            diff = TextureDiff.TextureDiff(os.path.join(oldFolder, oldEntry), 'old', os.path.join(newFolder, newEntry), 'new', maxTexelTolerance=_maxTexelTolerance, rmsTolerance=_rmsTolerance)
            if diff.IsDifferent():
                AddMappingChange(results, mappingName, MappingChangeType.ICON_CHANGED, each, oldFolder=oldFolder, oldValue=oldEntry, newFolder=newFolder, newValue=newEntry, diffData=diff)

    def _Sort(a, b):
        order = [MappingChangeType.ICON_CHANGED,
         MappingChangeType.ENTRY_ADDED,
         MappingChangeType.ICON_TYPE_ADDED,
         MappingChangeType.ENTRY_DELETED,
         MappingChangeType.ICON_TYPE_DELETED,
         MappingChangeType.ICON_NAME_CHANGED]
        indexA = order.index(a.changeType)
        indexB = order.index(b.changeType)
        if indexA < indexB:
            return -1
        elif indexA == indexB:
            return 0
        else:
            return 1

    results.sort(cmp=_Sort)
    return results


def GetConfluencePage(branch, pageTitle):
    user = os.getenv('CONFLUENCE_SCRIPT_USER', None)
    password = os.getenv('CONFLUENCE_SCRIPT_PASSWORD', None)
    if not user or not password:
        logger.warning('No user/password set for Confluence, skipping page generation')
        return (None, None, None, None)
    wiki = Confluence(user=user, password=password)
    spaceID = wiki.GetPageID(_confluenceSpaceKey, 'Dev')
    rootPageID = wiki.GetPageID(_confluenceSpaceKey, _confluenceRootPage)
    branchPageName = '%s - %s' % (branch, _confluenceRootPage)
    branchPageID = wiki.GetPageID(_confluenceSpaceKey, branchPageName)
    if branchPageID is None:
        branchPageID = wiki.CreatePage(_confluenceSpaceKey, branchPageName, parentPageID=rootPageID, notifyWatchers=False)
    pageID = wiki.GetPageID(_confluenceSpaceKey, pageTitle)
    if pageID is None:
        pageID = wiki.CreatePage(_confluenceSpaceKey, pageTitle, parentPageID=branchPageID, notifyWatchers=False)
    return (wiki,
     pageID,
     spaceID,
     branchPageID)


def UpdateConfluencePage(wiki, pageTitle, pageID, parentPageID, contents, deleteAttachments = False):
    if pageID is not None:
        if deleteAttachments:
            wiki.DeleteAllAttachments(pageID)
        wiki.UpdatePage(pageID, _confluenceSpaceKey, pageTitle, contents, parentPageID=parentPageID)
    return wiki.baseUrl + '/pages/viewpage.action?pageId=%s' % pageID


def GenerateConfluenceTableForMapping(wiki, pageID, mapping, changelist, outputFolder):
    contents = "<table width='100%'><tbody><tr>"
    contents += "<th colspan='4'><strong>%s</strong></th></tr>" % mapping
    if len(changelist) > 0:
        contents += '<tr><th>IDs</th><th>Change Type</th><th>Change Value</th><th>Preview</th></tr>'
        for change in changelist:
            contents += change.ToHtmlConfluenceTableRow(wiki, pageID, outputFolder)

    else:
        contents += "<tr><td colspan='4'>No changes.</td></tr>"
    contents += '</tbody></table>'
    return contents


def GenerateEmail(confluencePageUrl, branch, date):
    message = MIMEMultipart()
    message['Subject'] = '[%s]Image Server Icon Validation - %s' % (branch, date)
    message['From'] = _sender
    message['To'] = ', '.join(_mailRecipients)
    messageBody = MIMEText("<html><body><p><a href='%s'>Confluence Report</a></p></body></html>" % confluencePageUrl, 'html', 'utf-8')
    message.attach(messageBody)
    smtp_host = os.getenv('SMTP_HOST', 'exchis.ccp.ad.local')
    smtp_port = os.getenv('SMTP_PORT', '25')
    server = smtplib.SMTP(host=smtp_host, port=smtp_port)
    user = os.getenv('SMTP_USER', None)
    password = os.getenv('SMTP_PASSWORD', None)
    tls = os.getenv('SMTP_TLS', False)
    if tls:
        server.starttls()
    if user and password:
        server.login(user, password)
    logger.debug('Sending e-mail... Host=%s Port=%s User=%s Password=%s' % (smtp_host,
     smtp_port,
     user,
     password))
    logger.debug('Sender=%s, Receivers=%s' % (_sender, ', '.join(_mailRecipients)))
    server.sendmail(_sender, _mailRecipients, message.as_string())
    server.quit()


def SaveResultsToJson(allResults, folder, name):
    output = {}
    for mapping, changelist in allResults:
        output[mapping] = {}
        for change in changelist:
            for id in change.ids:
                if id not in output[mapping]:
                    output[mapping][id] = {}
                output[mapping][id] = change.ToDict()

    WriteMapping(output, folder, name)


def ParseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', default=False, action='store_true')
    parser.add_argument('--generateReport', default=False, action='store_true', help='If set, write the report in a confluence page.')
    parser.add_argument('--branchName', default=None, help='Name of the branch this is run in.')
    parser.add_argument('--previousBuildFolder', default=None, help='Root folder for the artifact of the previous build.')
    parser.add_argument('--newBuildFolder', default=None, help='Root folder for the artifact of the new build.')
    parser.add_argument('--outputFolder', default=None, help='Output folder for the diff icons generated and the output log.')
    return parser.parse_args()


if __name__ == '__main__':
    arguments = ParseArguments()
    logger = logging.getLogger('IconRendering_%s' % os.getpid())
    logging.basicConfig(level=logging.DEBUG if arguments.debug else logging.INFO)
    oldFolder = arguments.previousBuildFolder
    newFolder = arguments.newBuildFolder
    today = datetime.date.today()
    date = '%s/%s/%s' % (today.year, today.month, today.day)
    start = time.clock()
    allResults = []
    mappings = ['typeIDMapping',
     'typeIDMapping.zh',
     'alliancesMapping',
     'alliancesMapping.zh',
     'corpsFactionsMapping',
     'corpsFactionsMapping.zh',
     'charactersMapping',
     'charactersMapping.zh']
    for mapping in mappings:
        try:
            oldMapping = ReadMapping(oldFolder, mapping)
            newMapping = ReadMapping(newFolder, mapping)
            filter = '.zh' if 'zh' in mapping else None
            logger.info('Checking mapping %s...' % mapping)
            results = CompareMappings(mapping, oldFolder, oldMapping, newFolder, newMapping, filter)
            allResults.append((mapping, results))
            logger.info('Done. Found %s changes for mapping %s.' % (len(results), mapping))
        except Exception as e:
            logger.error('Failed to compare mapping %s. Error: %s' % (mapping, e.message))

    reportTitle = '%s - %s' % (arguments.branchName, date)
    if arguments.generateReport:
        wiki, pageID, spaceID, branchPageID = GetConfluencePage(arguments.branchName, reportTitle)
        if wiki:
            contents = ''
            for mapping, changelist in allResults:
                contents += GenerateConfluenceTableForMapping(wiki, pageID, mapping, changelist, arguments.outputFolder)

            confluencePageUrl = UpdateConfluencePage(wiki, reportTitle, pageID, branchPageID, contents)
            if len(_mailRecipients) > 0:
                GenerateEmail(confluencePageUrl, arguments.branchName, reportTitle)
        else:
            logger.warning('No wiki page or e-mail generated.')
    SaveResultsToJson(allResults, arguments.outputFolder, reportTitle.replace('/', '-'))
    end = time.clock()
    elapsed = end - start
    logger.info('All done. Total time : %.3f seconds' % elapsed)
