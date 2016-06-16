'''
@author: Damola Mabogunje <damola@mabogunje.net>
@summary: A Command Line Utility for Sick Notifications
    -  Sends notices by email
'''

import argparse;
import ConfigParser as configparser;
import smtplib;
import sys;
import subprocess;

from email.mime.text import MIMEText;
from email.mime.multipart import MIMEMultipart;
from time import strftime;
from datetime import datetime;

from symptoms import *;

try:
    import pygments;
    import markdown;
except ImportError:
        print 'This script requires pygements and markdown to be installed.';
        print 'Please:';
        print 'pip install pygments markdown or easy_install pygments markdown';
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
        print 'No template at %s. Please create one.' % template; 
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
    message = message % values;
    message = message.strip();

    # Convert to Stylized HTML
    css = subprocess.check_output(['pygmentize', '-S', 'default', '-f', 'html']);
    html = markdown.markdown(message, ['extra', 'codehilite']);
    html = '<style type="text/css">'+css+'</style>'+html;

    # Create Email
    email = MIMEMultipart('alternative');
    email['Subject'] = "Sick Notice (%s)" % datetime.today().strftime("%h %d %Y");
    email['From'] = CONFIG.get('USER', 'EMAIL');
    email['To'] = ', '.join(args.to);

    # Attach Plain Text and HTML versions
    email.attach(MIMEText(message, 'plain'));
    email.attach(MIMEText(html, 'html'));

    return email;

def notify(email, addresses):

    mailer = smtplib.SMTP(CONFIG.get('SICKLY', 'MAIL_SERVER'), CONFIG.get('SICKLY', 'PORT'));
    mailer.ehlo();
    mailer.starttls();
    mailer.ehlo();
    mailer.login(CONFIG.get('SICKLY', 'USERNAME'), CONFIG.get('SICKLY', 'PASSWORD'));
    mailer.sendmail(email['From'], addresses, email.as_string());
    mailer.close();

    print "Sick Notification Successfully Sent to %s" % addresses;


if __name__ =='__main__':
    # Get Default Configuration
    CONFIG_FILE = 'config.ini';
    CONFIG = configparser.ConfigParser();

    try:
        CONFIG.read(CONFIG_FILE);
        assert('USER' in CONFIG.sections());
        assert('SICKLY' in CONFIG.sections());
    except:
        print 'There is no configuration file at %s. Please create one first. See config.sample.ini for an example' % CONFIG_FILE;
        sys.exit(1);



    '''
    Process command-line arguments and email's a sick notification
    '''
    
    parser = argparse.ArgumentParser(description='Process notification arguments');

    parser.add_argument('-s', '--severity', metavar='1-4', nargs='?', 
                        default=str(SEVERITY.MEDIUM),
                        help='Severity of the symptom'
                       );

    parser.add_argument('-d', '--duration', metavar='TIME', type=int, nargs='?',
                        default=1,
                        help='Duration of the symptom. If < 0, duration <= abs(TIME), ' +
                        'else duration >= TIME'
                       );

    parser.add_argument('-t', '--template', nargs='?', default=CONFIG.get('SICKLY', 'TEMPLATE'),
                        required=False,
                        help='A Markdown Template to use for your email');

    parser.add_argument('-m', '--msg', nargs='?', default='NONE', help='Extra notes');
    parser.add_argument('to', nargs='+', help='Addresses to notify');

    args = parser.parse_args();
    
    try:
        symptom = parse_symptom(args);
    except IndexError:
        print "Severity ranges must be of the format 'min-max' i.e 1-2";
        sys.exit();
    except AssertionError:
        print "Severity out of range";
        sys.exit();
    else:
        email = compose_email(symptom, args.msg, args.template);
        
    try:
        notify(email, args.to);
    except Exception as error:
        print error;
        print 'Unable to send email';

