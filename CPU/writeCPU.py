#! /usr/bin/env python3
#Author: vk_en
#Linux
#Date: 1.09.2017 v.1.0
#   Есть еще команда "cat /proc/stat  |grep 'cpu'"  по ней инфы будет больше (https://www.kernel.org/doc/Documentation/filesystems/proc.txt)



import sys, re, aerodisk_ssh, json, time, os, sqlite3, datetime
import aerodisk_sqlite as sqlib
from subprocess import PIPE, Popen
dbPath = "/temp/CPU/cpu_stat.db"


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
    sqlib.execDB("CREATE TABLE 'stat' ( `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `users`	TEXT, `nice`	TEXT, `sys`	TEXT, `idle`	TEXT, `iowait`	TEXT, `steal`	TEXT, `times`	INTEGER)", patch)

def f_cpu():
    command = executeCmd("sar -u 3 1 |tail -1", raw=True)#Example ['Average:', 'all', '1.96\x00', '0.00\x00', '0.63\x00', '0.00\x00', '0.00\x00', '97.41\x00']
    command = command.replace(b"\x00", b"").decode(errors="replace").strip(" \n\t")
    state = re.findall(r"all\s+(\w*\.*\w*)\s+(\w*\.*\w*)\s+(\w*\.*\w*)\s+(\w*\.*\w*)\s+(\w*\.*\w*)\s+(\w*\.*\w*)", command)[0]
    sqlib.execDB(
        "INSERT INTO `stat` (users, nice, sys, iowait, steal, idle, times) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', {6});"
        .format(state[0], state[1], state[2], state[3], state[4], state[5], int(time.time())), dbPath)


if __name__ == "__main__":
    if os.path.exists(dbPath) != True:
        create_database(dbPath)
    startTime = time.time()
    c = 0
    while c <= 19 and time.time() - startTime < 57:
        f_cpu()
        c += 1

    del_time = int(time.time()) - 2592000
    sqlib.execDB("DELETE FROM stat WHERE times < '{0}'".format(del_time), dbPath)
