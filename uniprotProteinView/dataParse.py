import dataRetrieval
import pandas as pd
import random


def getFeaturesDataFrame(xmls, types):
    out = []
    typesSet = set(types)

    for nxml in xmls:
        features = [i for i in nxml if i.tag == '{http://uniprot.org/uniprot}feature']
        features = [features[i] for i, val in enumerate(features) if val.attrib['type'] in typesSet]
        name = [i.text for i in nxml if i.tag == '{http://uniprot.org/uniprot}name']
        xx = [None] * len(features)

        index = 0
        for feature in features:
            for feat in feature:
                if feat.tag == '{http://uniprot.org/uniprot}location':
                    begin = next((i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}begin'),
                                 -1)
                    end = next((i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}end'), -1)
                    position = next(
                        (i.attrib['position'] for i in feat if i.tag == '{http://uniprot.org/uniprot}position'), -1)
                    print(str(begin) + "  " + str(end) + '  ' + str(position))
                    xx[index] = dict(Name=name, Start=begin, Finish=end, color=f"#{random.randrange(0x1000000):06x}")
                index += 1

        out.append(xx)

    out = [i[0] for i in list(filter(None, out))]
    return pd.DataFrame(out)


