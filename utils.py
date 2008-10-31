# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

import os
import datetime

from email.MIMEText import MIMEText

SENDMAIL = '/usr/sbin/sendmail'

def send_mail(sender, recipients, subject, msg):
    """ Sends and email directly through the sendmail command. """
    for parametre in (sender, recipients, subject, msg):
        if not parametre:
            return 255
    msg = msg.encode('utf8')
    message = MIMEText(msg,'plain','utf-8')
    message['From'] = sender
    message['To'] = ', '.join(recipients)
    message['Subject'] = subject
    message['Date'] = datetime.datetime.now().strftime('%c')

    #print message.as_string()
    #status = 0

    p = os.popen("%s -t" % SENDMAIL, 'w')
    p.write(message.as_string())
    status = p.close()
    return status

if __name__ == "__main__":
    retour = send_mail('info@learngest.com',['jcbagneris@gmail.com',],'Essai 2', u'Contenu é à')
    print retour
