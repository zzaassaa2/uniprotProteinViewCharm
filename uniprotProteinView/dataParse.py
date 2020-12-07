import pandas as pd
import random
import re
import uniprotProteinView.dataRetrieval as dataRetrieval


def randomColor():
    return f"#{random.randrange(0x1000000):06x}"


def grepl(attrib, toTest):
    if 'description' in attrib:
        return toTest in attrib['description']
    else:
        return toTest in attrib['type']


def loopFeatures(features, name, offset, size, indent=True):
    xx = [None] * len(features)

    index = 0
    for tup in features:
        feature = tup[1]
        trueName = feature.attrib['description'] if 'description' in feature.attrib else feature.attrib['type']
        trueName = trueName[:30 - len(trueName)] + "..." if len(trueName) > 30 else trueName
        trueName = "    " + trueName if indent else trueName

        for feat in feature:
            if feat.tag == '{http://uniprot.org/uniprot}location':
                try:
                    begin = next((i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}begin'
                                  if 'position' in i.attrib),
                                 -1)
                    end = next((i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}end'
                                if 'position' in i.attrib), -1)
                    position = next(
                        (i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}position'
                         if 'position' in i.attrib), -1)
                except:
                    print("Break happened")
                    break
                if begin == -1 and end == -1:
                    if position == -1:
                        break
                    else:
                        begin = position
                        end = position
                elif begin == -1 or end == -1:  # For now, just scrape it
                    break

                if not begin.isnumeric():
                    if not end.isnumeric():
                        break  # scrape it
                    else:
                        begin = end
                elif not end.isnumeric():
                    if not begin.isnumeric():
                        break  # scrape it
                    else:
                        end = begin

                if begin == end:
                    begin = int(begin) - 1
                    end = int(end) + 1

                xx[index] = dict(ProtName=name, Name=trueName, Start=begin, Finish=end, yStart=offset,
                                 yStop=offset + size,
                                 Color=tup[0])
                index += 1
                break

    return xx


def fixColor(clrList):
    offset = 0
    out = [None] * len(clrList)
    for clr in clrList:
        if clr.startswith("random"):
            c = str(clr)
            c = c.replace("|", " ")
            c = c.split()
            number = [i for i in c if i.startswith("number")]

            if len(number) > 0:
                number = re.sub(r'^.*?:', '', number[0])
                number = int(number) if number.isnumeric() else 1
            else:
                number = 1

            if number != 1:
                toAppend = [None] * number
                out = out + toAppend

                for _ in range(number):
                    out[offset] = randomColor()
                    offset += 1
            else:
                out[offset] = randomColor()
                offset += 1
        else:
            out[offset] = clr
            offset += 1

    return out


def retrieveOutput(listIn):
    clr = []

    if isinstance(listIn, dict):
        if 'type' in listIn:
            t = listIn['type']
        else:
            t = [v for k, v in listIn.items()]

        if 'colors' in listIn:
            clr = listIn['colors']
    else:
        t = listIn

    if not isinstance(clr, list):
        clr = [clr]
    if not isinstance(t, list):
        t = [t]

    return [t, fixColor(clr)]


def getFeaturesDataFrame(xmls, types, dess, offsetIn, showProgress):
    out = []
    proteins = retrieveOutput(xmls)
    xmls = dataRetrieval.getProtein(proteins[0], showProgress)

    typesSet = retrieveOutput(types)
    dessSet = retrieveOutput(dess)
    offsetSet = retrieveOutput(offsetIn)

    chainClr = proteins[1]
    typesClr = typesSet[1]
    dessClr = dessSet[1]
    offsetClr = offsetSet[1]

    typesSet.extend(typesSet[0])
    dessSet = dessSet[0]
    offsetSet = offsetSet[0]

    offset = 0
    index = 0
    for nxml in xmls:
        features = [i for i in nxml if i.tag == '{http://uniprot.org/uniprot}feature']

        chainFeatures = [(chainClr[index] if index < len(chainClr) else randomColor(), val) for val in features
                         if val.attrib['type'] == 'chain']
        stdFeatures = [(typesClr[i] if i < len(typesClr) else randomColor(), val) for i, el in enumerate(typesSet)
                       for val in features if val.attrib['type'] == el]
        dessFeatures = [(dessClr[i] if i < len(dessClr) else randomColor(), val) for i, el in enumerate(dessSet)
                        for val in features if grepl(val.attrib, el)]
        offsetFeatures = [(offsetClr[i] if i < len(offsetClr) else randomColor(), val) for i, el in enumerate(offsetSet)
                          for val in features if val.attrib['type'] == el]

        name = next((i.text for i in nxml if i.tag == '{http://uniprot.org/uniprot}name'), "Cant find")

        if len(chainFeatures) > 0:
            out.extend(loopFeatures(chainFeatures, name, offset, 1, False))

        if len(stdFeatures) > 0:
            out.extend(loopFeatures(stdFeatures, name, offset, 1))

        if len(dessFeatures) > 0:
            out.extend(loopFeatures(dessFeatures, name, offset, 1))

        if len(offsetFeatures) > 0:
            offset += 1
            out.extend(loopFeatures(offsetFeatures, name, offset, 0.3))
            offset += 0.3
        else:
            offset += 1

        index += 1

    return pd.DataFrame(out)
