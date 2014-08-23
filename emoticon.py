#!/usr/bin/env python3
# encoding: utf-8

import json
import time
import sys
import sqlite3
try:
    from lxml import etree
except ImportError:
    import xml.etree.cElementTree as etree
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
try:
    import cPickle as pickle
except ImportError:
    import pickle
    
python_version = sys.version_info[0]

def download_file():
    url = 'https://raw.github.com/turingou/o3o/master/yan.json'
    data = urlopen(url).read()
    with open("yan.json", "wb") as f:
        f.write(data)


def update_file():
    ''' invokes file "time" to calculate update intervals '''
    last_updata_time = pickle.load(open("time_update_yan.json.txt", "rb"))
    time_now = time.time()

    if time_now - last_updata_time >= 604800:  # update yan.json weekly
        download_file()
        pickle.dump(time.time(), open("time_update_yan.json.txt", "wb"))


def parse(query):
    if query == '':
        conn = sqlite3.connect('history.sqlite3')
        c = conn.cursor()
        c.execute("SELECT emoticons from most_common")
        conn.commit()
        yans = c.fetchall()
        yans = [item for tup in yans for item in tup]
        conn.close()
        return yans
    else:
        if python_version >= 3:
            f = open("yan.json", encoding="UTF-8")
        else:
            f = open("yan.json")

        data = json.load(f)
        for chunk in data['list']:
            if query in chunk['tag']:
                return chunk['yan']
        f.close()


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


def history():
    query = sys.argv[1]
    conn = sqlite3.connect('history.sqlite3')
    c = conn.cursor()
    # max(len([emoticons])) = 33
    c.execute('''CREATE TABLE if NOT exists usage
            (emoticons char(50) PRIMARY KEY, hits INT(2048) DEFAULT 1)''')
    c.execute("CREATE TABLE if NOT exists most_common (emoticons char(50))")
    c.execute('''
    INSERT or REPLACE into usage (emoticons, hits) VALUES
    ("{0}",
    COALESCE(
        ((SELECT hits FROM usage WHERE emoticons="{0}") + 1),
        1)
    )'''.format(query))

    # invokes the file "time" to calculate update intervals
    last_updata_time = pickle.load(open("time_update_most_common.txt", "rb"))
    time_now = time.time()
    if time_now - last_updata_time >= 1209600:  # updating most_common once every other week
        pickle.dump(time.time(), open("time_update_most_common.txt", "wb"))

        conn = sqlite3.connect('history.sqlite3')
        c = conn.cursor()
        c.execute("DROP TABLE most_common")
        c.execute('''CREATE TABLE most_common
                (emoticons char(50) PRIMARY KEY, hits INT(2048) DEFAULT 1)''')
        c.execute('''INSERT INTO most_common
                SELECT emoticons,hits from usage
                ORDER BY hits DESC
                LIMIT 10''')
        c.execute("DROP TABLE usage")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    update_file()
    history()
    query = ''.join([i for i in sys.argv[1] if i.isalpha()]) # strip
    to_xml(query)
