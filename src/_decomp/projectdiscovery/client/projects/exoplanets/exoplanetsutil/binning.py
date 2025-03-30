#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetsutil\binning.py


def bin(data, fidelity):
    if not data or fidelity is None:
        return data
    flux = map(lambda x: x[1], data)
    time = map(lambda x: x[0], data)
    binSize = fidelity
    if binSize == 1:
        return data
    newFlux = [ sum(flux[binSize * i:binSize * i + binSize]) / binSize for i in range(len(flux) / binSize) ]
    newTime = [ sum(time[binSize * i:binSize * i + binSize]) / binSize for i in range(len(time) / binSize) ]
    if len(flux) % binSize != 0:
        lastElementsIndex = -(len(flux) % binSize)
        newFlux.append(sum(flux[lastElementsIndex:]) / len(flux[lastElementsIndex:]))
        newTime.append(sum(time[lastElementsIndex:]) / len(time[lastElementsIndex:]))
    return zip(newTime, newFlux)
