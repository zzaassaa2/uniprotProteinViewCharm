from xml.etree import ElementTree as ET
import requests
from tqdm import tqdm
import os
import sys
import re


def getLocal(fileName):
    tree = ET.ElementTree(file=fileName)
    root = tree.getroot().findall('.//{http://uniprot.org/uniprot}entry')
    if len(root) > 0:
        return root
    else:
        Warning('Attempted to load file: ' + fileName + ", however the file either doesn't exist or isn't in the "
                                                        "proper format")
        return None


def getRemote(source, url=None, returnGet=False):
    if url is None:
        if source.endswith(".xml"):
            url = "https://www.uniprot.org/uniprot/" + source
        else:
            url = "https://www.uniprot.org/uniprot/" + source + ".xml"

    get = requests.get(url)
    code = get.status_code

    if code == 200:
        if returnGet:
            return get.content
        else:
            tree = ET.fromstring(get.content)
            root = tree.findall('.//{http://uniprot.org/uniprot}entry')
            return root
    elif code == 400:
        Warning("Bad request. There is a problem with input: " + source)
    elif code == 404:
        Warning("Not found. The resource you requested, " + source + " doesn't exist")
    elif code == 410:
        Warning("Gone. The resource you requested, " + source + " was removed")
    elif code == 500:
        Warning("Internal server error. Most likely a temporary problem, but if the problem persists please contact "
                "Uniprot services")
    elif code == 503:
        Warning("Service not available. The server is being updated, try again later.")
    else:
        Warning("Unknown error return: " + str(code) + ", using the input: " + source)

    return None


def getRemoteDownload(source):
    if source.endswith(".xml"):
        source = source[:-4]

    get = getRemote(source, returnGet=True)
    if get:
        fileName = './' + source + '.xml'
        with open(fileName, 'w') as r:
            r.write(get.decode("utf-8"))

        return getLocal(fileName)

    return get


def getRandomProtein(orgID):
    k = requests.get("https://www.uniprot.org/uniprot/?query=reviewed:yes+AND+organism:" + str(orgID) + "&random=yes")
    return getRemote(None, url=k.url + ".xml")


def getData(s, out, offset, pbar=None):
    s = s.strip()
    flag = pbar is not None
    if s.startswith("random"):
        if flag:
            pbar.set_description_str("Retrieving random protein(s)")
        s = s.replace("|", " ")
        s = s.split()
        number = [i for i in s if i.startswith("number")]
        orgid = [i for i in s if i.startswith("orgid")]

        if len(number) > 0:
            number = re.sub(r'^.*?:', '', number[0])
            number = int(number) if number.isnumeric() else 1
        else:
            number = 1

        if len(orgid) > 0:
            orgid = re.sub(r'^.*?:', '', orgid[0])
            orgid = int(orgid) if orgid.isnumeric() else 1
        else:
            orgid = 9606

        if number != 1:
            toAppend = [None] * number
            out = out + toAppend

            for _ in range(number):
                out[offset] = getRandomProtein(orgid)
                offset += 1
                if flag:
                    pbar.update(1 / number)
        else:
            out[offset] = getRandomProtein(orgid)
            offset += 1
    elif os.path.isdir(s):
        if flag:
            pbar.set_description("Retrieving files from directory")
        found = [os.path.join(s, file) for file in os.listdir(s) if file.endswith(".xml")]
        toAppend = [None] * (len(found) - 1)
        out = out + toAppend

        for fou in found:
            out[offset] = getLocal(fou)
            offset += 1
    elif os.path.isfile(s):
        if flag:
            pbar.set_description("Loading local protein xml data")
        out[offset] = getLocal(s)
        offset += 1
    else:
        if flag:
            pbar.set_description("Attempting remote download")
        if s.endswith(".xml"):
            print("Failed to find file: " + s + ". Would you like to attempt to download the file?")
            print("Enter 1 for yes, 2 for no and skip this file, 3 to force terminate process.")
            get = input("Command: ").strip()

            if get == 1:
                out[offset] = getRemoteDownload(s)
            elif get == 3:
                sys.exit("Forced termination as user requested")
        else:
            out[offset] = getRemote(s)
        offset += 1

    return offset, out


def getProtein(sources, showProgress=True):
    if isinstance(sources, list):
        out = [None] * len(sources)
    else:
        sources = [sources]
        out = [None]

    offset = 0
    if showProgress:
        with tqdm(total=len(sources)) as pbar:
            for s in sources:
                tup = getData(s, out, offset, pbar)
                offset = tup[0]
                out = tup[1]

                pbar.update(1)
    else:
        for s in sources:
            tup = getData(s, out, offset)
            offset = tup[0]
            out = tup[1]

    return [i[0] for i in list(filter(None, out))]
