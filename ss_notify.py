'''
@author: Damola Mabogunje
@contact: damola@mabogunje.net
@summary: An automated sick notification system -  sends sick notices by email
'''

import sys
import argparse
import smtplib

class SEVERITY:
    '''
    Enumeration representing symptom severity
    '''

    (LOW, MILD, MEDIUM, SEVERE) = range(1,5);

class RSVP:
    '''
    Enumeration representing the possibility of attending class
    '''
    
    (TRUE, FALSE, UNCERTAIN) = range(0,3);

class Symptom:
    '''
    Data Structure for storing symptom parameters
    '''

    def __init__(self, severity, duration):
        self.severity = {'CURRENT': SEVERITY.LOW, 'PREDICTED': SEVERITY.MEDIUM };
        self.duration = 0;

    def get_effect(self):
        
        if (self.severity['CURRENT'] + self.severity['PREDICTED']) < (2 * SEVERITY.MEDIUM):
            return RSVP.TRUE;

        #TO DO

    def __str__(self):

        #TO DO


'''
Processes command-line arguments and email's a sick notification
'''
if __name__ =='__main__':
    parser = argparse.ArgumentParser(description='Process notification arguments');

    parser.add_argument('-s', '--severity', metavar='[0-4]', nargs='?', 
                        default=str(SEVERITY.MEDIUM), 
                        help='Severity of the symptom (0=low, 4=severe)'
                       );

    parser.add_argument('-t', '--duration', metavar='TIME', type=int, nargs='?',
                        help='Duration of the symptom. If TIME < 0, duration < 0, ' +
                        'else if TIME > 0, duration >= 0'
                       );

    parser.add_argument('to', metavar='EMAIL_ADDRESSES', nargs='+',
                        help='Addresses to notify'
                       );

    #TO DO
