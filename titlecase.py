#!/usr/bin/env python

'''
@author: Jacob Vlijm, Damola Mabogunje <damola@mabogunje.net>
@summary: A Command Line Tool for Renaming Files in a Folder in
          Title Case.
@see: http://askubuntu.com/questions/589296/recursively-rename-all-files-and-folders-to-title-case-from-terminal
'''

import os;
import sys;
import shutil;
import argparse;
import ast;

try:
    from configobj import ConfigObj;
except Exception as err:
    print err;
    print 'This script requires the ConfigObj library to run. See http://www.voidspace.org.uk/python/configobj.html.';
    sys.exit(1);

def exclude_words(name):
    for item in SKIP:
        name = name.replace(" "+item.title()+" ", " "+item.lower()+" ")

    # on request of OP, added a replace option for parethesis etc.
    for key, value in REPLACE.iteritems():
        name = name.replace(key, value)
    
    return name

if __name__ == '__main__':

    # Get Default Configuration
    SCRIPT_DIR = os.path.dirname( os.path.realpath(__file__) );
    CONFIG_FILE = SCRIPT_DIR + '/config.ini';
    CONFIG = ConfigObj(CONFIG_FILE);

    try:
        assert('TITLECASE' in CONFIG);
        assert('IGNORABLE_WORDS' in CONFIG['TITLECASE']);
        assert('DANGEROUS_CHARS' in CONFIG['TITLECASE']);
    except Exception as err:
        print err
        print 'The configuration file at %s is either missing or incomplete. ' % CONFIG_FILE;
        print 'Please create one properly first.';
        print 'See config.sample.ini for an example.';
        
        sys.exit(1);

    SKIP = CONFIG['TITLECASE']['IGNORABLE_WORDS'].strip().split(',');
    REPLACE = CONFIG['TITLECASE']['DANGEROUS_CHARS'];

    # Setup Command Line Parser
    parser = argparse.ArgumentParser(description='Convert all nested file / subfolder names of a DIRECTORY into Title Case');

    parser.add_argument('-d', '--directory', nargs='?', default = os.path.abspath(__file__),
            help='Directory to rename files of')

    args = parser.parse_args();

for root, dirs, files in os.walk(args.directory):
    for f in files:
        split = f.find(".")

        if split not in (0, -1):
            name = ("").join((f[:split].lower().title(), f[split:].lower()))
        else:
            name = f.lower().title()

        name = exclude_words(name)
        shutil.move(root+"/"+f, root+"/"+name)
        print f, ' -> ', name;

for root, dirs, files in os.walk(args.directory):
    for dr in dirs:
        name = dr.lower().title()
        name = exclude_words(name)
        shutil.move(root+"/"+dr, root+"/"+name)
