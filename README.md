# rbk_nas_validate
A project to validate a NAS Backup on Rubrik

This script walks a tree on a NAS client and compares that tree to a backed up fileset on Rubrik. By default it will only show
missing files/diretories and errors while walking the tree (e.g. permission problems).  For a full report of all files and
directories, turn on verbose mode with -v.

<pre>
Usage: rbk_nas_validate.py [-hDlv] [-c creds] [-b backup] [-d date] [-f fileset] [-o output_file] local_path rubrik
-h | --help : Prints this message
-D | --DEBUG : Prints debug information
-l | --latest : Use the latest backup
-v | --versboe : Verbose output.  Shows validated files
-c | --creds= : Specify Rubrik credentials [user:password
-b | --backup= : Specify the Rubrik backup [host:share]
-d | --date= : Specify datestamp of backup
-f | --fileset= : Specify fileset of backup
-o | --outfile= : Send output to a file
local_path : Local Path of NAS share
rubrik: Name or IP of Rubrik cluster
</pre>

Any of the inputs not specified on the command line will cause the script to prompt the user. 
The format for the date is "YY-MM-DD HH:MM:SS".  Use quotes due to the space.  Or use -l for the latest backup.

The output is a csv format.
