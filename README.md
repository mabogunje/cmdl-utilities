# Command Line Utilities (CMDL-Utilities)

 CMDL-Utilities is a suite of various command-line scripts I've written for myself over time.
 Each script in this library draws on configurations specified in a config.ini file at the
 root level.

## Utilities
 
1.  __Sickly__:  
    A script for sending automated sick notices by email. Your emails can be customized by changing
    the defaut markdown template provided at sickly/templates/default.md or creating your own.

        Run ./sickly.py -h for more.

2.  __Trashmail__:  
    A script for deleting/archiving old mail in you mailbox. You can specify how old the mail must be 
    (in days), and what folder it should be archived to (Trash by default). You can also decide
    whether to delete the mail permanently or not. By default your mails are kept.

        Run ./trashmail.py -h for more.

## License

These utilities are provided under the [GNU LGPL PUBLIC LICENSE V3](http://www.gnu.org/licenses/lgpl-3.0-standalone.html) or later.
See COPYING.md & COPYING.LESSER.md for details. 
