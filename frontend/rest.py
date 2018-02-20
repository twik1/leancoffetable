import requests
import json


class CurlREST:
    def __init__(self):
        self.headers = {'Content-Type':'application/json'}
        self.baseurl = 'http://localhost:5000/lct/api/v1.0/'

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


    def gettopics(self, boardid):
        datastore = {}
        datastore['data'] = []
        datastore['ctrl'] = {}
        datastore['vote'] = []
        board = self.get(self.baseurl + 'boards/' + boardid)
        if 'datalist' in board:
            datastore['ctrl']['user'] = board['datalist'][0]['user']

        ids = self.get(self.baseurl+"boards/"+boardid+'/topics')
        datastore['ctrl']['response'] = ids['response']

        if 'datalist' in ids:
            for id in ids['datalist']:
                topic = self.get(self.baseurl+'boards/'+boardid+'/topics/'+str(id['topicid']))
                datastore['data'].append(topic['datalist'][0])
                #vids = ids = self.get(self.baseurl+"boards/"+boardid+'/topics/'+str(id['topicid'])+'/votes')

        return datastore
