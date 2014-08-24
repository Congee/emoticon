#!/usr/bin/env python3
# encoding: utf-8

from emoticon import json, pickle, sqlite3, sys, time

create_table_usage='''
CREATE TABLE if NOT exists usage
(emoticons char(50) PRIMARY KEY, hits INT(2048) DEFAULT 1)'''

create_table_most_common='''
CREATE TABLE IF NOT EXISTS most_common
(emoticons char(50) PRIMARY KEY, hits INT(2048) DEFAULT 1)'''

drop_table_most_common='''DROP TABLE most_common;'''
drop_table_usage='''DROP TABLE usage;'''

build_table_most_common='''
INSERT INTO most_common
SELECT emoticons,hits from usage
ORDER BY hits DESC
LIMIT 10;'''

update_emoticon_into_usage='''
INSERT or REPLACE into usage (emoticons, hits) VALUES
(?,
COALESCE(
    ((SELECT hits FROM usage WHERE emoticons=?) + 1),
    1)
);'''


def calculate_update_interval():
    '''invokes the file "time" to calculate update intervals'''
    last_updata_time = pickle.load(open("time_update_most_common.txt", "rb"))
    time_now = time.time()
    if time_now - last_updata_time >= 1209600:  # updating most_common once every other week
        pickle.dump(time.time(), open("time_update_most_common.txt", "wb"))
        return True
    return False


def history(query):
    conn = sqlite3.connect('history.sqlite3')
    c = conn.cursor()
    # max(len([emoticons])) = 33
    c.execute(create_table_usage)
    c.execute(update_emoticon_into_usage,(query,query))
    c.execute(drop_table_most_common)
    c.execute(create_table_most_common)
    c.execute(build_table_most_common)

    if calculate_update_interval():
        c.execute(drop_table_most_common)
        c.execute(create_table_most_common)
        c.execute(build_table_most_common)
        c.execute(drop_table_usage)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    query = sys.argv[1]
    history(query)
