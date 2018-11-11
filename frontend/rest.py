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
        """
        Executes REST API call to specific url
        :param url:
            The url to do a get towards
        :return:
            A dictionary with {response: <result of the http get>,
            if successful a list of dictionaries
        """
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

    def getboards(self, param):
        """
        Get boards available for user
        :param param:
            A datastructure to fill in for the function
        :return:
            The result of the REST http get request
            ToDo: we can add more respons if something fail
        """
        ids = self.get(self.baseurl+"boards")
        param['ctrl']['response'] = ids['response']
        if 'datalist' in ids:
            for id in ids['datalist']:
                board = self.get(self.baseurl+'boards/'+str(id['boardid']))
                param['data'].append(board['datalist'][0])
        return ids['response']

    def getuser(self, param, user):
        usr = self.get(self.baseurl + "users/" + user)
        param['ctrl']['response'] = usr['response']
        if 'datalist' in usr:
            param['data'].append(usr['datalist'][0])
        return usr['response']

    def adduser(self, data):
        usr = self.post(self.baseurl + "users", data)
        return usr['response']

    def updateuser(self, data):
        return self.adduser(data)

    def gettopics(self, boardid, datastore):
        """
        Get all topic data for a specific boardid

        :param boardid:
            Id of a specific board <1>
        :param datastore:
            A dictionary of {ctrl:{loggedin:<yes/no>, sessionname:<twik>,boardid:<1>}
        :return:
            More parameters for datastore
            {ctrl:{votenum:<3>,boardname:<name>,
            {data:{
        """
        datastore['data'] = []
        index = 0
        board = self.get(self.baseurl + 'boards/' + boardid)
        datastore['ctrl']['votenum'] = board['datalist'][0]['votenum']
        datastore['ctrl']['boardname'] = board['datalist'][0]['name']
#        if 'datalist' in board:
#            datastore['ctrl']['user'] = board['datalist'][0]['user']

        ids = self.get(self.baseurl+"boards/"+boardid+'/topics')
        datastore['ctrl']['response'] = ids['response']

        myvote = 0  # Total number of votes for me of the entire board
        if 'datalist' in ids:
            for id in ids['datalist']:  # Loop through topics
                #thumbsup = 0
                numvote = 0  # Total number of votes for each topic
                topic = self.get(self.baseurl+'boards/'+boardid+'/topics/'+str(id['topicid']))
                datastore['data'].append(topic['datalist'][0])
                # Handle votes
                vids = self.get(self.baseurl+"boards/"+boardid+'/topics/'+str(id['topicid'])+'/votes')
                if 'datalist' in vids:
                    myvotes = 0  # Total number of of votes for me for each topic
                    for ids in vids['datalist']:
                        vote = self.get(self.baseurl+"boards/"+boardid+'/topics/'+str(id['topicid'])+'/votes/'+str(ids['voteid']))
                        #if 'datalist' in vote:
                        if 'sessionname' in datastore['ctrl']:
                            if datastore['ctrl']['sessionname'] == vote['datalist'][0]['user']:
                                #datastore['data'][index]['thumbsup'] = str(ids['voteid'])
                                myvotes = myvotes + 1
                                myvote = myvote + 1
                        numvote = numvote + 1
                    datastore['data'][index]['myvotes'] = myvotes
                datastore['data'][index]['numvote'] = numvote
                index = index + 1
        # Only sort on request
        #sortedlist = self.sortlist(datastore['data'])
        #datastore['data'] = sortedlist
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

    def delvote(self, boardid, topicid, voteid, username):
        if voteid == '0':
            vids = self.get(self.baseurl + "boards/" + boardid + '/topics/' + topicid + '/votes')
            if 'datalist' in vids:
                for ids in vids['datalist']:
                    vote = self.get(self.baseurl + "boards/" + boardid + '/topics/' + topicid + '/votes/' + str(ids['voteid']))
                    if username == vote['datalist'][0]['user']:
                        voteid = str(ids['voteid'])
                        break
        self.delete(self.baseurl + "boards/" + boardid + "/topics/" + topicid + "/votes/" + voteid)
