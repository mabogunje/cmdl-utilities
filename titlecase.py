#!/usr/bin/env python

'''
@author: Jacob Vlijm, Damola Mabogunje <damola@mabogunje.net>
@summary: A Command Line Tool for Renaming Files in a Folder in
          Title Case.
@see: http://askubuntu.com/questions/589296/recursively-rename-all-files-and-folders-to-title-case-from-terminal
'''

import os
import sys
import shutil

directory = sys.argv[1]

SKIP = ["a", "an", "the", "and", "but", "or", "nor", "at", "by", "for", "from", "in", "into", "of", "off", "on", "onto", "out", "over", "to", "up", "with", "as"];
REPLACE = [["(", "["], [")", "]"], ["{", "["], ["}", "]"]];

def exclude_words(name):
    for item in SKIP:
        name = name.replace(" "+item.title()+" ", " "+item.lower()+" ")

    # on request of OP, added a replace option for parethesis etc.
    for item in REPLACE:
        name = name.replace(item[0], item[1])
    
    return name

for root, dirs, files in os.walk(directory):
    for f in files:
        split = f.find(".")
        if split not in (0, -1):
            name = ("").join((f[:split].lower().title(), f[split:].lower()))
        else:
            name = f.lower().title()
        name = exclude_words(name)
        shutil.move(root+"/"+f, root+"/"+name)

for root, dirs, files in os.walk(directory):
    for dr in dirs:
        name = dr.lower().title()
        name = exclude_words(name)
        shutil.move(root+"/"+dr, root+"/"+name)
