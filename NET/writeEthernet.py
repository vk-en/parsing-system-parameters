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
dbPath = "/temp/NET/ethernet_stat.db"
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
    sqlib.execDB("CREATE TABLE `stat` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `times`	INTEGER, `name` TEXT, `read_speed` TEXT, `read_iops` TEXT, `write_speed` TEXT, `write_iops` TEXT, `util` TEXT)", patch)


def convertToMegabytes(value):
    '''Converts GBs and KBs to MBs.'''
    if value[len(value)-1]=="M":
        conv_val = value[0:len(value)-1]
    elif value[len(value)-1]=="G":
        conv_val = str(round(float(value[0:len(value)-1]) * 1024,2))
    elif value[len(value)-1]=="K":
        conv_val = str(round(float(value[0:len(value)-1]) / 1024,4))
    else:
        conv_val = str(round(float(value) / 1024, 4))
    return conv_val



def f_ether():
    command = executeCmd("sudo sar -n DEV 3 2", raw=True)
    command = command.replace(b"\x00", b"").decode(errors="replace").strip(" \n\t")
    command = command.split('IFACE')
    average = command[3].split('\n')
    del average[0]
    result = []
    for stroka in average:
        delimetr = stroka.split()
        if delimetr[1] != "lo":
            #               name                  read mb/s               read IOPS               write mb/s            write iops      util
            result.append((delimetr[1], convertToMegabytes(delimetr[5]), delimetr[3], convertToMegabytes(delimetr[4]), delimetr[2], delimetr[9]))

    for add in result:
        sqlib.execDB("INSERT INTO `stat` ( times, name, read_speed, read_iops, write_speed, write_iops, util) VALUES ({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}');"
                     .format(int(time.time()), add[0], add[1], add[2], add[3], add[4], add[5]), dbPath)

if __name__ == "__main__":
    if os.path.exists(dbPath) != True:
        create_database(dbPath)
    startTime = time.time()
    c = 0
    while c <= 6 and time.time() - startTime < 57:
        f_ether()
        c += 1
        time.sleep(3.5)

    del_time = int(time.time()) - 2592000
    sqlib.execDB("DELETE FROM stat WHERE times < '{0}'".format(del_time), dbPath)
