import requests
import json


class CurlREST:
    def __init__(self):
        self.headers = {'Content-Type':'application/json'}
        self.baseurl = 'http://localhost:5000/lct/api/v1.0/'

    def sortlist(self, list):
        if len(list) == 0:
            #Nothing to sort
            return list
        newlist = []
        i = 0
        j = 0
        lowest = list[0]['numvote']
        while len(list) > 0:
            for i in range(0, len(list)):
                if list[i]['numvote'] <= lowest:
                    lowest = list[i]['numvote']
                    j = i
            newlist.insert(0,list[j])
            del list[j]
            if len(list)>=1:
                lowest = list[0]['numvote']
                j = 0
        return newlist


    def get(self, url):
        response = {}
        try:
            ret = requests.get(url, headers=self.headers)
            response['response'] = ret.status_code
            if ret.status_code == 200:
                response['datalist'] = ret.json()
            return response
        except requests.exceptions.RequestException as e:
            response['response'] = 0
            return response


    def post(self, url, param):
        response = {}
        try:
            ret = requests.post(url, headers=self.headers, data=json.dumps(param))
            response['response'] = ret.status_code
            return response
        except requests.exceptions.RequestException as e:
            response['response'] = 0
            return response


    def delete(self, url):
        response = {}
        try:
            ret = requests.delete(url, headers=self.headers)
            response['response'] = ret.status_code
            return response
        except requests.exceptions.RequestException as e:
            response['response'] = 0
            return response


    def getboards(self):
        datastore = {}
        datastore['data'] = []
        datastore['ctrl'] = {}
        ids = self.get(self.baseurl+"boards")
        datastore['ctrl']['response'] = ids['response']
        if 'datalist' in ids:
            for id in ids['datalist']:
                board = self.get(self.baseurl+'boards/'+str(id['boardid']))
                datastore['data'].append(board['datalist'][0])
        return datastore


    def gettopics(self, boardid, datastore):
        datastore['data'] = []
        index = 0
        board = self.get(self.baseurl + 'boards/' + boardid)
        datastore['ctrl']['votenum'] = board['datalist'][0]['votenum']
        datastore['ctrl']['boardname'] = board['datalist'][0]['name']
#        if 'datalist' in board:
#            datastore['ctrl']['user'] = board['datalist'][0]['user']

        ids = self.get(self.baseurl+"boards/"+boardid+'/topics')
        datastore['ctrl']['response'] = ids['response']

        myvote = 0
        if 'datalist' in ids:
            for id in ids['datalist']:
                thumbsup = 0
                numvote = 0
                topic = self.get(self.baseurl+'boards/'+boardid+'/topics/'+str(id['topicid']))
                datastore['data'].append(topic['datalist'][0])
                # Handle votes
                vids = self.get(self.baseurl+"boards/"+boardid+'/topics/'+str(id['topicid'])+'/votes')
                if 'datalist' in vids:
                    for ids in vids['datalist']:
                        vote = self.get(self.baseurl+"boards/"+boardid+'/topics/'+str(id['topicid'])+'/votes/'+str(ids['voteid']))
                        #if 'datalist' in vote:
                        if 'sessionname' in datastore['ctrl']:
                            if datastore['ctrl']['sessionname'] == vote['datalist'][0]['user']:
                                datastore['data'][index]['thumbsup'] = str(ids['voteid'])
                                myvote = myvote + 1
                        numvote = numvote + 1
                datastore['data'][index]['numvote'] = numvote
                index = index + 1
        sortedlist = self.sortlist(datastore['data'])
        datastore['data'] = sortedlist
        datastore['ctrl']['myvote'] = myvote
        return datastore

    def checkuser(self, user):
        ids = self.get(self.baseurl + "users/" + user)
        if ids['response'] == 200:
            return True
        else:
            return False

    def getconfig(self, param):
        ids = self.get(self.baseurl+"config")
        param['ctrl']['response'] = ids['response']
        if 'datalist' in ids:
            param['data'] = ids['datalist']
        return param


