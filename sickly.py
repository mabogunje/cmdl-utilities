'''
@author: Damola Mabogunje
@contact: damola@mabogunje.net
@summary: An automated sick notification system -  sends sick notices by email
'''

import argparse;
import smtplib;
import sys;
import subprocess;

from email.mime.text import MIMEText;
from email.mime.multipart import MIMEMultipart;
from time import strftime;
from datetime import datetime;

from config import *;
from symptoms import *;

try:
    import pygments;
    import markdown;
    import cfgparse;
except ImportError:
        print 'This script requires pygements and markdown and cfgparse to be installed.';
        print 'Please:';
        print 'pip install pygments markdown cfgparse or easy_install pygments markdown cfgparse';
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
    template = open(template, 'r');
    message = template.read();
    
    values = { "status": symptom.status(),
               "duration": symptom.duration(),
               "forecast": symptom.forecast(),
               "time": symptom.respite().capitalize(),
               "rsvp": symptom.effect(),
               "msg": msg,
               "user": CONFIG.get('USER')
             };
    message = message % values;
    message = message.strip();

    css = subprocess.check_output(['pygmentize', '-S', 'default', '-f', 'html']);
    html = markdown.markdown(message, ['extra', 'codehilite']);
    html = '<style type="text/css">'+css+'</style>'+html;

    email = MIMEMultipart('alternative');
    email['Subject'] = "Sick Notice (%s)" % datetime.today().strftime("%h %d %Y");
    email['From'] = CONFIG.get('EMAIL');
    email['To'] = ', '.join(args.to);

    email.attach(MIMEText(message, 'plain'));
    email.attach(MIMEText(html, 'html'));
    return email;

def notify(email, addresses):

    mailer = smtplib.SMTP(CONFIG.get('SERVER'), CONFIG.get('PORT'));
    mailer.ehlo();
    mailer.starttls();
    mailer.ehlo();
    mailer.login(CONFIG.get('USERNAME'), CONFIG.get('PASSWORD'));
    mailer.sendmail(email['From'], addresses, email.as_string());
    mailer.close();

    print "Sick Notification Successfully Sent to %s" % addresses;


if __name__ =='__main__':
    '''
    Processes command-line arguments and email's a sick notification
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

    parser.add_argument('-t', '--template', nargs='?', default=CONFIG.get('TEMPLATE'),
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

