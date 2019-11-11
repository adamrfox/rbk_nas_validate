#!/usr/bin/python
from __future__ import print_function
import sys
import os
import getopt
import getpass
import rubrik_cdm
import urllib3
urllib3.disable_warnings()
import datetime
import pytz

def usage():
    print ("Usage goes here")
    exit(0)


def python_input (message):
    if sys.version < 3:
        value = input (message)
    else:
        value = raw_input(message)
    return (value)

def dprint (message):
    if DEBUG:
        print(message)


if __name__ == "__main__":
    user = ""
    password = ""
    DEBUG = False
    outfile = ""
    host = ""
    fileset = ""
    share = ""
    date = ""
    backup = ""
    latest = False
    snap_list = []


    optlist,args = getopt.getopt(sys.argv[1:], 'hDc:b:d:f:l', ['--help', '--DEBUG', '--creds=', '--backup=', '--date=', '--fileset=', '--latest'])
    for opt, a in optlist:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('-D', '--DEBUG'):
            DEBUG = True
        if opt in ('-c', '--creds'):
            (user, password) = a.split(':')
        if opt in ('-b', '--backup'):
            backup = a
        if opt in ('-d', '--date'):
            date = a
        if opt in ('-f', '--fileset'):
            fileset = a
        if opt in ('-l', '--latest'):
            latest = True

    (local_path, rubrik_addr) = args
    if not backup:
        backup = python_input("Backup (host:share): ")
    if not fileset:
        fileset = python_input ("Filset: ")
    if not user:
        user = python_input("User: ")
    if not password:
        password = getpass.getpass("Password: ")
    (host, share) = backup.split(':')
    if share.startswith('/'):
        delim = "/"
    else:
        delim = "\\"

    rubrik = rubrik_cdm.Connect(rubrik_addr, user, password)
    rubrik_config = rubrik.get('v1','/cluster/me')
    rubrik_tz = rubrik_config['timezone']['timezone']
    local_zone = pytz.timezone(rubrik_tz)
    utz_zone = pytz.timezone('utc')
    hs_data = rubrik.get('internal', '/host/share')
    for x in hs_data['data']:
        if x['hostname'] == host and x['exportPoint'] == share:
            share_id = x['id']
            break
    if share_id == "":
        sys.stderr.write("Share not found\n")
        exit(2)
    dprint("Share ID: " + share_id)
    fs_data = rubrik.get('v1', str("/fileset?share_id=" + share_id + "&name=" + fileset + "&primary_cluster_id=local"))
    fs_id = fs_data['data'][0]['id']
    dprint("FSID: " + fs_id)
    snap_data = rubrik.get('v1', str("/fileset/" + fs_id))
    for snap in snap_data['snapshots']:
        s_time = snap['date']
        s_id = snap['id']
        s_time = s_time[:-5]
        snap_dt = datetime.datetime.strptime(s_time, '%Y-%m-%dT%H:%M:%S')
        snap_dt = pytz.utc.localize(snap_dt).astimezone(local_zone)
        snap_dt_s = snap_dt.strftime('%Y-%m-%d %H:%M:%S')
        snap_list.append((s_id, snap_dt_s))
    if latest:
        snap_id = snap_list[-1][0]
    else:
        for i, snap in enumerate(snap_list):
            print (str(i) + ": " + snap[1] + "  [" + snap[0] + "]")
        valid = False
        while not valid:
            snap_index = python_input("Select Backup: ")
            try:
                snap_id = snap_list[int(snap_index)][0]
            except (IndexError, TypeError, ValueError) as e:
                print ("Invalid Index: " + str(e))
                continue
            valid = True
    dprint("SnapID: " + snap_id)
    for dirName, subDirList, fileList in os.walk(local_path):
        print("DIR: " + dirName)
        for fname in fileList:
            print ("\t " + fname)








