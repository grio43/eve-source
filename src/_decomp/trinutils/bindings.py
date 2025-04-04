#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinutils\bindings.py
import logging
import osutils.subst as subst
import trinity
logger = logging.getLogger(__name__)

def FindBrokenBindingReferences(trinObj):
    brokenBindings = []
    bindings = trinObj.Find('trinity.TriValueBinding')
    for binding in bindings:
        if not binding.sourceObject:
            brokenBindings.append(binding)
        if not binding.destinationObject:
            if not binding.name.startswith('self_') and not binding.name.startswith('new_') and not binding.name.startswith('old_'):
                brokenBindings.append(binding)
        elif binding.destinationObject.GetRefCounts()[1] == 2:
            brokenBindings.append(binding)

    return brokenBindings


def FindBrokenBindings(trinObj):
    return [ x.name for x in FindBrokenBindingReferences(trinObj) ]


def HasBrokenBindings(trinObj):
    brokenBindings = FindBrokenBindings(trinObj)
    return len(brokenBindings) > 0


def FixBrokenBindings(trinObj):
    curveSets = trinObj.Find('trinity.TriCurveSet')
    allBindings = trinObj.Find('trinity.TriValueBinding')
    deleteCs = []
    knownUsedCurves = []
    deleteBinds = []
    for cs in curveSets:
        for binding in cs.bindings:
            if not binding.destinationObject or not binding.sourceObject:
                deleteBinds.append(binding)
            elif binding.destinationObject.GetRefCounts()[1] == 2:
                deleteBinds.append(binding)
            else:
                knownUsedCurves.append(binding.sourceObject)

        for d in deleteBinds:
            logger.info('Deleting binding: %s' % d.name)
            cs.bindings.remove(d)

    for cs in curveSets:
        deleteCurves = []
        for curve in cs.curves:
            if curve not in knownUsedCurves:
                usedElsewhere = False
                for b in allBindings:
                    if b.sourceObject == curve and b not in deleteBinds:
                        usedElsewhere = True
                        logger.info('Curve found being used outside its curveset: %s' % curve.name)
                        break

                if not usedElsewhere:
                    deleteCurves.append(curve)

        for d in deleteCurves:
            logger.info('Deleting curve: %s' % d.name)
            cs.curves.remove(d)

    for cs in curveSets:
        if not cs.curves and not cs.bindings:
            deleteCs.append(cs)

    for d in deleteCs:
        if hasattr(trinObj, 'curveSets'):
            for cs in trinObj.curveSets:
                if d == cs:
                    logger.info('Deleting curve set: %s' % d.name)
                    trinObj.curveSets.remove(d)
                    continue

    return trinObj


def RepairFile(filePath):
    filePath = subst.GetUnsubstedPath(filePath)
    logger.info('==== File:%s====' % filePath)
    original = trinity.Load(filePath)
    if original:
        if HasBrokenBindings(original):
            logger.info('Broken bindings found!')
            new = FixBrokenBindings(original)
            trinity.Save(new, filePath)
        else:
            logger.info('No broken bindings found!')
