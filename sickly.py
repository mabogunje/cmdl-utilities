#!/usr/bin/env python
# Created by [Damola Mabogunje](http://mabogunje.net/)

'''
@author: Damola Mabogunje <damola@mabogunje.net>
@summary: A Command Line Utility for Sick Notifications
    -  Sends notices by email
'''

import argparse;
import configparser;
import smtplib;
import subprocess;
import sys;

from os.path import dirname, realpath;
from email.message import EmailMessage;
from time import strftime;
from datetime import datetime;

from sickly.symptoms import *;

try:
    import pygments;
    import markdown;
except ImportError as err:
        print(err);
        print('This script requires pygments and markdown to be installed.');
        print('Please:');
        print('pip install pygments markdown or easy_install pygments markdown');

        sys.exit(0);

def parse_symptom(args):
    '''
    Make Symptom from arguments
    '''

    if args.severity:
        if len(args.severity) > 1:
            args.severity.index('-');
            values = [ int(x) for x in args.severity.split('-') ];

            assert (int(values[0]) >= SEVERITY.MILD) and (int(values[len(values)-1]) <= SEVERITY.SEVERE);
            return Symptom( (values[0], values[len(values)-1]), args.duration);
        else:
            return Symptom( (int(args.severity), int(args.severity)), args.duration);
    else:
        return Symptom();

def compose_email(symptom, msg, template):
    '''
    Creates email notification using template in plain text and HTML
    '''

    # Read in Markdown Template
    try:
        template = open(template, 'r');
    except IOError:
        print(f'No template at {template}. Please create one.'); 
        sys.exit(1);

    message = template.read();
    
    # Populate template with values
    values = { "status": symptom.status(),
               "duration": symptom.duration(),
               "forecast": symptom.forecast(),
               "time": symptom.respite().capitalize(),
               "rsvp": symptom.effect(),
               "msg": msg,
               "user": CONFIG.get('USER', 'NAME')
             };
    message = message.format(**values);
    message = message.strip();

    # Convert to Stylized HTML
    html = """\
            <!DOCTYPE html>
            <html>
                <head>
                    <style type="text/css">
                    {css}
                    </style>
                </head>
                <body>
                    {message}
                </body>
            </html>
            """
    css = subprocess.check_output(['pygmentize', '-S', 'default', '-f', 'html']);
    markup = markdown.markdown(message, extensions=['extra', 'codehilite']);
    content = {"css": css.decode(), "message": markup}
    html = html.format(**content)

    # Create Email
    email = EmailMessage();
    email['Subject'] = "Sick Notice {}".format(datetime.today().strftime("%h %d %Y"));
    email['From'] = CONFIG.get('USER', 'EMAIL');
    email['To'] = ', '.join(args.to);

    email.set_content(message); # Plain text version
    email.add_alternative(html, subtype="html") # HTML Version

    return email;

def notify(email, addresses):

    print('Connecting to the SMTP Server...');

    with smtplib.SMTP(CONFIG.get('SICKLY', 'MAIL_SERVER'), CONFIG.get('SICKLY', 'PORT')) as server:
        
        server.ehlo(); # Identify yourself to the server
        server.starttls(); # Initiate Secure Connection
        server.ehlo(); # Reidentify yourself over secure connection

        # Login and Send Email
        server.login(CONFIG.get('SICKLY', 'USERNAME'), CONFIG.get('SICKLY', 'SECRETKEY'));
        server.send_message(email);

    print(f"Sick Notification Successfully Sent to {addresses}");


if __name__ =='__main__':

    # Get Default Configuration
    SCRIPT_DIR = dirname( realpath(__file__) );
    CONFIG_FILE = SCRIPT_DIR + '/config.ini';
    CONFIG = configparser.ConfigParser();

    try:
        CONFIG.read(CONFIG_FILE);
        assert('USER' in CONFIG.sections());
        assert('SICKLY' in CONFIG.sections());
        assert(CONFIG.get('SICKLY', 'TEMPLATE'));
    except Exception as err:
        print(f'The configuration file at {CONFIG_FILE} is either missing or incomplete. ');
        print('Please create one properly first.');
        print('See config.sample.ini for an example.');
        
        sys.exit(1);

    # Setup Command Line Parser
    parser = argparse.ArgumentParser(description='Email a Sick Notice about the SEVERITY of your symptoms TO one or more email addresses',
            add_help=True);

    parser.add_argument('-s', '--severity', metavar='SEVERITY: 1=Mild | 2=Medium | 3=Severe', nargs='?', 
                        default=str(SEVERITY.MEDIUM),
                        help='Severity of the symptom'
                       );

    parser.add_argument('-d', '--duration', metavar='DURATION (in hours)', type=int, nargs='?',
                        default=1,
                        help='Duration of symptom in hours. -1 means < 1hr'
                       );

    parser.add_argument('-t', '--template', nargs='?', metavar='TEMPLATE',

                        default='/'.join((SCRIPT_DIR, CONFIG.get('SICKLY', 'TEMPLATE'))),
                        required=False,
                        help='A Markdown Template to use for your email');

    parser.add_argument('-m', '--msg', nargs='?', default='NONE', help='Extra notes');
    parser.add_argument('to', nargs='+', help='Email Addresses to notify');

    args = parser.parse_args();
    
    # Parse Arguments and Compose Email
    try:
        symptom = parse_symptom(args);
    except IndexError:
        print("Severity ranges must be of the format 'min-max' i.e 1-2");
        sys.exit();
    except AssertionError:
        print("Severity out of range");
        sys.exit();
    else:
        email = compose_email(symptom, args.msg, args.template);

    # Send Email Notification
    try:
        notify(email, args.to);
    except Exception as error:
        print(error);
        print('Unable to send email');

