#! /usr/bin/env python3
#Author: vk_en
#Linux
#Date: 1.09.2017 v.1.0

#   Есть еще команда "cat /proc/meminfo"  по ней вывода будет больше


import sys, re, aerodisk_ssh, json, time, os, sqlite3, datetime
import aerodisk_sqlite as sqlib
from subprocess import PIPE, Popen
dbPath = "/temp/MEM/memory_stat.db"


def executeCmd(cmd, raw=False, tout=15):
    '''Python 3 version. Automatically decodes input to UTF-8 and removes unnecessary symbols from the end of str. v2.5 22.06.2017'''
    try:
        proc = Popen(cmd, stdout=PIPE,stderr=PIPE, shell=True)
        out = proc.communicate(timeout=tout)[0]
    except TimeoutError:
        return 2
    except:
        return 1
    if raw:
        return out
    return out.decode(errors="replace").strip(" \n\t")


def create_database(patch):
    con = sqlite3.connect(patch)
    con.close()
    sqlib.execDB("CREATE TABLE `stat` (`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `_total`	INTEGER, `_used`	INTEGER, `_free`	INTEGER, `_shared`	INTEGER, `_buffers`	INTEGER, `_cached`	INTEGER, `buf_ca_used`	INTEGER, `buf_ca_free`	INTEGER, `swap_total`	INTEGER, `swap_used`	INTEGER, `swap_free`	INTEGER,`times`	INTEGER)", patch)


def f_mem():
    command = executeCmd("sudo sudo free -m").split('\n')
    del command[0]
    result = []
    for pa in command:
        result.append(pa.split())
    sqlib.execDB('INSERT INTO `stat` (_total, _used, _free, _shared, _buffers, _cached, buf_ca_used, buf_ca_free, swap_total, swap_used, swap_free, times) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11});'
                 .format(int(result[0][1]),
                         int(result[0][2]),
                         int(result[0][3]),
                         int(result[0][4]),
                         int(result[0][5]),
                         int(result[0][6]),
                         int(result[1][2]),
                         int(result[1][3]),
                         int(result[2][1]),
                         int(result[2][2]),
                         int(result[2][3]),
                         int(time.time())), dbPath)


if __name__ == "__main__":
    if os.path.exists(dbPath) != True:
        create_database(dbPath)
    startTime = time.time()
    c = 0
    while c <= 29 and time.time() - startTime < 58:
        f_mem()
        c += 1
        time.sleep(2)

    del_time = int(time.time()) - 2592000
    sqlib.execDB("DELETE FROM stat WHERE times < '{0}'".format(del_time), dbPath)
