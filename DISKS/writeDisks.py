#! /usr/bin/env python3
#Author: vk_en
#Linux
#Date: 4.09.2017 v.1.0


import sys, re, aerodisk_ssh, json, time, os, sqlite3, datetime
import aerodisk_sqlite as sqlib
from subprocess import PIPE, Popen
from socket import gethostname
hostname = gethostname()
curPath = os.path.dirname(os.path.realpath(__file__))
dbPath = "/temp/DISKS/disks_stat.db"
arg = sys.argv[:]

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
    sqlib.execDB("CREATE TABLE 'stat' (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `times` INTEGER, `name` TEXT, `read_speed` TEXT, `read_iops`	TEXT, `write_speed` TEXT, `write_iops` TEXT, `util` TEXT, `remoute` INTEGER)", patch)


def f_disk():
    command = executeCmd("sudo iostat -x 4 2 -Nm", raw=True)
    command = command.replace(b"\x00", b"").decode(errors="replace").strip(" \n\t")
    command = command.split('Device')
    result = command[2].split('\n')
    res_d_st = []
    del result[0]
    for stroka in result:
        delenie = stroka.split()
        if "5000" in delenie[0]:
           res_d_st.append((delenie[0], delenie[1], delenie[2], delenie[3], delenie[4], delenie[15], 0))

    #For Engine-1
    # if len(arg) == 1:
    #     remote_hostname = "ENGINE-1" if hostname == "ENGINE-0" else "ENGINE-0"
    #     rState = aerodisk_ssh.execute(remote_hostname, 'sudo ' + curPath + 'writeDisks.py ssh', timeout=30).split('\n')
    #     for a in rState:
    #         rea = a.split(';')
    #         res_d_st.append((rea[0], rea[3], rea[1], rea[4], rea[2], rea[5], 1))

    times = int(time.time())
    if len(arg) == 1:
        for add in res_d_st:
            sqlib.execDB(
                "INSERT INTO `stat` ( times, name, read_speed, read_iops, write_speed, write_iops, util, remoute) VALUES ({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7});"
                .format(times,
                        add[0],
                        add[3],
                        add[1],
                        add[4],
                        add[2],
                        add[5], add[6]), dbPath)
    else:
        for add in res_d_st:
            print("{0};{1};{2};{3};{4};{5};1".format(add[0], add[3], add[1], add[4], add[2], add[5]))



if __name__ == "__main__":
    if os.path.exists(dbPath) != True:
        create_database(dbPath)
    startTime = time.time()
    c = 0
    while c <= 6 and time.time() - startTime < 57:
        f_disk()
        c += 1
        time.sleep(5)


    del_time = int(time.time()) - 2592000
    sqlib.execDB("DELETE FROM stat WHERE times < '{0}'".format(del_time), dbPath)

