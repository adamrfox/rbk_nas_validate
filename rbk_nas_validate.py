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
import re


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

def vprint (message):
    if VERBOSE or DEBUG:
        print (message)

def write_output (fh, message):
    if fh:
        fh.write(message + "\n")
    else:
        print(message)


def validate_file (file, fs_id, snap_id):
    found = False
    f_search = rubrik.get('v1', '/fileset/' + fs_id + '/search?path=' + file, timeout=60)
    for f_inst in f_search['data']:
        if f_inst['path'] == file:
            for snap in f_inst['fileVersions']:
                if snap['snapshotId'] == snap_id:
                    found = True
                    break
    return(found)

if __name__ == "__main__":
    user = ""
    password = ""
    DEBUG = False
    VERBOSE = False
    outfile = ""
    host = ""
    fileset = ""
    share = ""
    date = ""
    backup = ""
    latest = False
    snap_list = []
    outfile = ""
    fh = ""

    optlist,args = getopt.getopt(sys.argv[1:], 'hDc:b:d:f:lvo:', ['--help', '--DEBUG', '--creds=', '--backup=', '--date=', '--fileset=', '--latest', '--verbose', '--outfile'])
    for opt, a in optlist:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('-D', '--DEBUG'):
            DEBUG = True
            VERBOSE = True
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
        if opt in ('-v', '--verbose'):
            VERBOSE = True
        if opt in ('-o', '--outfile'):
            outfile = a
            fh = open(outfile, "w+")

    (local_path, rubrik_addr) = args
    mp_regex = r"^" + re.escape(local_path)
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
        if not local_path.endswith(delim):
            local_path += delim
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
        subDirList[:] = [d for d in subDirList if ".snapshot" not in d and "~snapshot" not in d]
        for dir in subDirList:
            name = dirName + delim + dir
            file_inst = re.sub(mp_regex, '', name)
            if not file_inst.startswith(delim):
                file_inst = delim + file_inst
            valid = validate_file(file_inst, str(fs_id), str(snap_id))
            out_message = name + ',' + str(valid)
            if not valid or (valid and VERBOSE):
                write_output (fh, out_message)
        for file in fileList:
            name = dirName + delim + file
            file_inst = re.sub(mp_regex, '', name)
            if not file_inst.startswith(delim):
                file_inst = delim + file_inst
            valid = validate_file(file_inst, str(fs_id), str(snap_id))
            out_message = name + ',' + str(valid)
            if not valid or (valid and VERBOSE):
                write_output (fh, out_message)
'''
    for f in files.keys():
        found = False
        f_search = rubrik.get('v1', '/fileset/' + str(fs_id) + '/search?path=' + str(files[f]))
        for f_inst in f_search['data']:
            if f_inst['path'] == files[f]:
                for snap in f_inst['fileVersions']:
                    if snap['snapshotId'] == snap_id:
                        found = True
                        break
        print (f + " : " + str(found))
'''
