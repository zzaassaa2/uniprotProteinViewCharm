import pandas as pd
import random


def grepl(lis, li, parse):
    if parse in lis:
        pattern = lis[parse]
    else:
        return False

    for var in li:
        if var in pattern:
            return True
    return False


def loopFeatures(features, name, offset, size):
    xx = [None] * len(features)

    index = 0
    for feature in features:
        trueName = feature.attrib['description']
        for feat in feature:
            if feat.tag == '{http://uniprot.org/uniprot}location':
                begin = next((i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}begin'),
                             -1)
                end = next((i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}end'), -1)
                position = next(
                    (i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}position'), -1)
                if begin == -1 and end == -1:
                    if position == -1:
                        break
                    else:
                        begin = position
                        end = position
                elif begin == -1 or end == -1:  # For now, just scrape it
                    break

                if begin == end:
                    begin = int(begin) - 1
                    end = int(end) + 1

                xx[index] = dict(ProtName=name, Name=trueName, Start=begin, Finish=end, yStart=offset, yStop=offset+size,
                                 Color=f"#{random.randrange(0x1000000):06x}")
                index += 1
                break

    return xx


def getFeaturesDataFrame(xmls, types, dess, offsetIn):
    out = []
    typesSet = set(types)
    dessSet = set(dess)
    offsetSet = set(offsetIn)

    offset = 0
    for nxml in xmls:
        features = [i for i in nxml if i.tag == '{http://uniprot.org/uniprot}feature']
        stdFeatures = [features[i] for i, val in enumerate(features) if val.attrib['type'] in typesSet or
                    grepl(val.attrib, dessSet, 'description')]
        offsetFeatures = [features[i] for i, val in enumerate(features) if val.attrib['type'] in offsetSet]
        name = next((i.text for i in nxml if i.tag == '{http://uniprot.org/uniprot}name'), "Cant find")

        if len(stdFeatures) > 0:
            out.extend(loopFeatures(stdFeatures, name, offset, 1))

        if len(offsetFeatures) > 0:
            offset += 1
            xx = loopFeatures(offsetFeatures, name, offset, 0.3)
            # print(xx)
            # print(out)
            out.extend(xx)
            # print(out)
            offset += 0.3
        else:
            offset += 1

    return pd.DataFrame(out)
