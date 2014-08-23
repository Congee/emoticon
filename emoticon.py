#!/usr/bin/env python3
# encoding: utf-8

import json
import time
import sys
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    from lxml import etree
except ImportError:
    import xml.etree.cElementTree as etree


def download_file():
    url = 'https://raw.github.com/turingou/o3o/master/yan.json'
    data = urlopen(url).read()
    with open("yan.json", "wb") as f:
        f.write(data)


def update_file():
    ''' invokes file "time" to calculate update intervals '''
    last_updata_time = pickle.load(open("time", "rb"))
    time_now = time.time()

    if time_now - last_updata_time >= 432000:  # update yan.json weekly
        download_file()
        pickle.dump(time.time(), open("time", "wb"))


def parse(query):
    with open("yan.json", encoding="UTF-8") as f:
        data = json.load(f)
        for chunk in data['list']:
            if query in chunk['tag']:
                return chunk['yan']


def to_xml(query):
    '''
    <?xml version="1.o">
    <items>
        <item arg="laugh">
            <title>laugh</title>
            <subtitle>...</subtitle>
            <icon>icon.png</icon>
        </item>
    </items>
    '''
    yans = parse(query)
    root = etree.Element("items")
    for yan in yans:
        item = etree.Element("item", attrib={"arg": yan})
        title = etree.Element("title")
        title.text = query

        subtitle = etree.Element("subtitle")
        subtitle.text = yan

        icon = etree.Element("icon")
        icon.text = 'icon.png'

        item.extend([title, subtitle, icon])
        root.append(item)

    print(etree.tostring(root, xml_declaration=True, pretty_print=True).decode())


if __name__ == '__main__':
    update_file()
    query = sys.argv[1]
    to_xml(query)
