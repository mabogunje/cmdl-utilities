#!/usr/bin/env python

'''
@authors: Radek Wojcik, Damola Mabogunje <damola@mabogunje.net>
@summary: A Command Line Utility for Deleting Old Emails.
    - It builds on Radek Wojcik's work.
@see: http://radtek.ca/blog/delete-old-email-messages-programatically-using-python-imaplib/ 
'''

import argparse;
import ConfigParser as configparser;
import getpass;
import imaplib;
import datetime;

from os.path import dirname, realpath;

def connect_imap(server, mailbox, password):
    m = imaplib.IMAP4_SSL(server)  # server to connect to
    print("{0} Connecting to mailbox via IMAP...".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")));
    m.login(mailbox, password);
 
    return m;
 
def move_to_trash_before_date(m, folder, trash, days_before):
    no_of_msgs = int(m.select(folder)[1][0])  # required to perform search, m.list() for all lables, '[Gmail]/Sent Mail'
    print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))
 
 
    before_date = (datetime.date.today() - datetime.timedelta(days_before)).strftime("%d-%b-%Y")  # date string, 04-Jan-2013
    typ, data = m.search(None, '(BEFORE {0})'.format(before_date))  # search pointer for msgs before before_date
 
    if data != ['']:  # if not empty list means messages exist
        no_msgs_del = data[0].split()[-1]  # last msg id in the list
        print("- Marked {0} messages for removal with dates before {1} in '{2}'.".format(no_msgs_del, before_date, folder))

        # Move to Trash
        m.copy("1:{0}".format(no_msgs_del), trash)  # copy to trash
        m.store("1:{0}".format(no_msgs_del), '+FLAGS.SILENT', '\\DELETED'); # mark original for deletion
        m.expunge(); # delete original
        print("{0} messages moved to {1}".format(no_msgs_del, trash))
    else:
        print("- Nothing to remove.")
 
    return
 
def empty_folder(m, folder, do_expunge=True):
    print("- Empty '{0}' & Expunge all mail...".format(folder))
    m.select(folder)  # select all trash
    m.store("1:*", '+FLAGS', '\\Deleted')  # Flag all Trash as Deleted
    if do_expunge:  # See Gmail Settings -> Forwarding and POP/IMAP -> Auto-Expunge
        m.expunge()  # not need if auto-expunge enabled
    else:
        print("Expunge was skipped.")
    return
 
def disconnect_imap(m):
    print("{0} Done. Closing connection & logging out.".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
    m.close()
    m.logout()
    return
 
class PasswordAction(argparse.Action):
    def __call__ (self, parser, namespace, values, option_string=None):
        mypass = getpass.getpass();
        setattr(namespace, self.dest, mypass);

if __name__ == '__main__':

    # Get Default Configuration
    SCRIPT_DIR = dirname( realpath(__file__) );
    CONFIG_FILE = SCRIPT_DIR + '/config.ini';
    CONFIG = configparser.ConfigParser();

    try:
        CONFIG.read(CONFIG_FILE);
        assert('USER' in CONFIG.sections());
        assert('TRASHMAIL' in CONFIG.sections());
    except Exception as err:
        print err
        print 'The configuration file at %s is either missing or incomplete. ' % CONFIG_FILE;
        print 'Please create one properly first.';
        print 'See config.sample.ini for an example.';

        sys.exit(1);
    
    # Setup Command Line Parser
    parser = argparse.ArgumentParser(description='Move Old Emails in a FOLDER in your MAILBOX at SERVER to TRASH',
            add_help=True);
    
    parser.add_argument('-s', '--server', nargs='?', default=CONFIG.get('TRASHMAIL', 'MAIL_SERVER'),
            help='Email Host Server')

    parser.add_argument('-m', '--mailbox', nargs='?',
            help='Email account to access', default=CONFIG.get('TRASHMAIL', 'MAILBOX'));

    parser.add_argument('-f', '--folder', nargs='?',required=True, 
            help='Email folder to clean');

    parser.add_argument('-t', '--trash', nargs='?', default=CONFIG.get('TRASHMAIL', 'TRASH_FOLDER'),
            help='Your Email Trash Folder');

    parser.add_argument('-b', '--before', type=int, nargs='?', default=CONFIG.get('TRASHMAIL', 'BEFORE'),
            help='Delete messages older than this number of days');

    parser.add_argument('-p', '--password', action=PasswordAction, nargs=1, required=True, 
            help='Password to your email account');

    remove_parser = parser.add_mutually_exclusive_group(required=False);
    remove_parser.add_argument('--force', dest='remove', action='store_true', help='Delete from server completely'); 
    remove_parser.add_argument('--save', dest='remove', action='store_false', help='Save deleted items in the Trash folder');
    
    parser.set_defaults(remove=False);
    args = parser.parse_args();


    # Connect to account with specified args and delete/archive email
    m_con = connect_imap(args.server, args.mailbox, args.password);
    move_to_trash_before_date(m_con, args.folder, args.trash, args.before)  # folder cleanup
 
    if(args.remove): 
        empty_folder(m_con, args.trash, do_expunge=True);  # can send do_expunge=False, default True
 
    disconnect_imap(m_con);
