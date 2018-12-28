import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# gmail (smtp.gmail.com:587)
# To be able to use with gmail you need to allow
# less secure app access in security options
#
# live (smtp.live.com:587)
# 

class mailSMTP:
    def __init__(self, ip="", port=587, user="", password="", mfrom=""):
        self.set_param(ip, port, user, password, mfrom)

    def set_param(self, ip, port, user, password, mfrom):
        # Check validity e.g mfrom
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.mfrom = mfrom

    def test_conn(self):
        if self.ip is None:
            return True
        try:
            self.server = smtplib.SMTP(self.ip, self.port, timeout=1)
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
            self.server.login(self.user, self.password)
            self.server.quit()
            return False
        except Exception as e:
            return True
            
    def send(self, dest, subj, body):
        if self.ip is None:
            return True
        try:
            self.server = smtplib.SMTP(self.ip, self.port)
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
            self.server.login(self.user, self.password)
            msg = MIMEMultipart()
            msg['From'] = self.mfrom
            msg['To'] = dest
            msg['Subject'] = subj
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            self.server.sendmail(self.mfrom, dest, text)
            self.server.quit()
            return False
        except:
            return True

#    def set_config(self, cfgstore):
#        self.ip = cfgstore['Mail host']['mail_host']
#        self.port = int(cfgstore['Mail host port']['mail_port'])
#        self.user = cfgstore['Mail username']['mail_user']
#        self.password = cfgstore['Mail password']['mail_password']

    def set_min_config(self, cfgstore):
        self.ip = cfgstore['mail_host']
        if not cfgstore['mail_port'] == "":
            self.port = int(cfgstore['mail_port'])
        else:
            self.port = 0
        self.user = cfgstore['mail_user']
        self.password = cfgstore['mail_password']

    def get_config(self):
        cfgstore = {'Mail host': {'mail_host': self.ip},
                        'Mail host port': {'mail_port': str(self.port)},
                        'Mail username': {'mail_user': self.user},
                        'Mail password': {'mail_password': self.password},
                        }
        return cfgstore
