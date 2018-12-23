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
    def __init__(self, ip, port, user, password, mfrom):
        self.set_param(ip, port, user, password, mfrom)

    def set_param(self, ip, port, user, password, mfrom):
        # Check validity e.g mfrom
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.mfrom = mfrom

    def test_conn(self):
        try:
            self.server = smtplib.SMTP(self.ip, self.port)
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
            self.server.login(self.user, self.password)
            self.server.quit()
            return False
        except:
            return True
            
    def send(self, dest, subj, body):
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


