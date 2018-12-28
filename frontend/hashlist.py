import datetime
import hashlib
import time
import threading


# {user:, hash:, dateandtime:, hours:}
class Hashlist:
    def __init__(self, seed):
        self.hashlist = []
        self.seed = seed
        self.thread = threading.Thread(target=self.work)
        self.thread.start()

    def work(self):
        while True:
            for entry in self.hashlist:
                end = entry['dateandtime'] + datetime.timedelta(hours=entry['hours'])
                if datetime.datetime.now() > end:
                    self.hashlist.remove(entry)
            time.sleep(60)

    def create(self, email, user, hours):
        # Check if user already have an active entry
        for entry in self.hashlist:
            if entry['email'] == email:
                return
        # No active entry
        listentry = {}
        listentry['email'] = email
        listentry['user'] = user
        inputstr = "{}{}{}".format(email, str(datetime.datetime.now()),str(self.seed))
        listentry['hash'] = hashlib.sha256(inputstr.encode('utf-8')).hexdigest()
        listentry['dateandtime'] = datetime.datetime.now()
        listentry['hours'] = hours
        self.hashlist.append(listentry)
        return listentry['hash']

    def checkhash(self, usrhash):
        for entry in self.hashlist:
            if entry['hash'] == usrhash:
                return entry['user']
        return False

    def removehash(self, usrhash):
        for entry in self.hashlist:
            if entry['hash'] == usrhash:
                self.hashlist.remove(entry)
