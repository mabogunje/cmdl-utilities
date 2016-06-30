'''
@author: Damola Mabogunje
@contact: damola@mabogunje.net
@summary: This package contains Sickle Cell symptom definitions
'''

class SEVERITY:
    '''
    Enumeration representing symptom severity
    '''

    (MILD, MEDIUM, SEVERE) = range(1,4);

    def str(self, severity):

        severity_map = { SEVERITY.MILD: "MILD",
                         SEVERITY.MEDIUM: "MEDIUM",
                         SEVERITY.SEVERE: "SEVERE"
                       };

        return severity_map.get(severity);

class RSVP:
    '''
    Enumeration representing the possibility of attending class
    '''
    
    (TRUE, FALSE, UNCERTAIN) = range(0,3);

    def str(self, rsvp):

        effect_map = { RSVP.TRUE: "YES",
                       RSVP.FALSE: "NO",
                       RSVP.UNCERTAIN: "MAYBE",
                     };

        return effect_map.get(rsvp);

class Symptom:
    '''
    Data Structure for storing symptom parameters
    '''

    def __init__(self, severity=(SEVERITY.MILD, SEVERITY.MEDIUM), duration=1):
        self.severity = {'CURRENT': severity[0], 'PREDICTED': severity[1] };
        self.timespan = duration;

    def compute_effect(self):
        '''
        Returns the machine-readable effect of the severity of symptom on attendance
        '''

        if abs(self.timespan) > 2:
            return RSVP.FALSE;

        if (self.severity['PREDICTED'] - self.severity['CURRENT']) >= SEVERITY.MILD:
            return RSVP.UNCERTAIN;
        elif (self.severity['CURRENT'] + self.severity['PREDICTED']) < (2 * SEVERITY.MEDIUM):
            return RSVP.TRUE;
        else:
            return RSVP.FALSE;

    def respite(self):
        '''
        Returns the human-readable recovery time necessary for the symptom
        '''

        if self.compute_effect() is RSVP.FALSE:
            respite = "the rest of the day";
        elif self.compute_effect() is RSVP.TRUE:
            respite = "1 hour (at least)" if (abs(self.timespan) > 1) else "1 hour (at most)";
        else:
            respite = "Unknown";
        
        return respite;

    def effect(self):
        '''
        Returns the human-readable effect of the severity of symptom on attendance
        '''

        return RSVP().str( self.compute_effect() );

    def status(self):
        '''
        Returns the human-readable current severity of symptom
        '''

        return SEVERITY().str( self.severity['CURRENT'] );

    def forecast(self):
        '''
        Returns the human-readable predicted severity of symptom
        '''

        return SEVERITY().str( self.severity['PREDICTED'] );

    def duration(self):
        '''
        Returns the human-readable time span of the symptom
        '''

        format = '%s %d hour(s)';

        if(self.timespan < 0):
            return format % ('under', abs(self.timespan));
        else:
            return format % ('over', abs(self.timespan));

    def __str__(self):

        delta_str = "\n";

        if (self.status() != self.forecast()):
            delta_str = "\nMight become %s\n" % self.forecast(); 

        format = "Ongoing %(severity_now)s symptoms of %(duration)s.\
                %(delta)s\
                Time to recover: %(respite)s\n\
                Attending class? %(effect)s";

        values = { 'severity_now': self.status(),
                   'duration': self.duration(),
                   'delta': delta_str,
                   'respite': self.respite(),
                   'effect': self.effect()
                  };

        return format % values;

