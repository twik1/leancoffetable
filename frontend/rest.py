import requests
import json


class CurlREST:
    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}
        # self.baseurl = 'http://localhost:5000/lct/api/v1.0/'

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
            ret = requests.get(url, headers=self.headers, timeout=3)
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

    def setbaseurl(self, address, port):
        self.baseurl = 'http://' + address + ':' + port + '/lct/api/v1.0/'

    def getboards(self):
        """
        Get boards available for user
        :return:
            A dictionary retlist with results
            {'data':[<id1>, <id2>]
             'result': <result of the HTTP request>
            }
        """
        retlist = {'data':[]}
        ids = self.get(self.baseurl+"boards")
        retlist['result'] = ids['response']
        if 'datalist' in ids:
            for id in ids['datalist']:
                retlist['data'].append(str(id['boardid']))
        return retlist

    def addboard(self, data):
        """
        Add a board
        :param data:
            a dictionary with board data
        :return:
            A dictionary retlist with results
            {'result': <result of the HTTP request>}
        """
        retlist = {}
        res = self.post(self.baseurl + "boards", data)
        retlist['result'] = res['response']
        return retlist

    def getboard(self, boardid):
        """
        Get data for a specific board id
        :param boardid:
        :return:
            A dictionary retlist with results
            {'data':[<board data>]
             'result': <result of the HTTP request>
            }
        """
        retlist = {'data': []}
        board = self.get(self.baseurl + 'boards/' + boardid)
        retlist['result'] = board['response']
        if 'datalist' in board:
            retlist['data'].append(board['datalist'][0])
        return retlist

    def delboard(self, boardid):
        """
        Delete a specific board id
        :param boardid:
        :return:
        """
        retlist = {}
        res = self.delete(self.baseurl + 'boards/' + boardid)
        retlist['result'] = res['response']
        return retlist

    def getusers(self):
        """
        Get all userids
        :return:
            A dictionary retlist with results
            {'data':[<usr1>, <usr2>]
             'result': <result of the HTTP request>
            }
        """
        retlist = {'data': []}
        usrs = self.get(self.baseurl + "users")
        retlist['result'] = usrs['response']
        if 'datalist' in usrs:
            for usr in usrs['datalist']:
                retlist['data'].append(usr['user'])
        return retlist

    def getuser(self, user):
        """
        Get data for a specific userid
        :param user:
            A dictionary retlist with results
            {'data':[<user data>]
             'result': <result of the HTTP request>
            }
        """
        retlist = {'data': []}
        usr = self.get(self.baseurl + "users/" + user)
        retlist['result'] = usr['response']
        if 'datalist' in usr:
            retlist['data'].append(usr['datalist'][0])
        return retlist

    def adduser(self, data):
        """
        Add a user
        :param data:
             A dictionary with user data
        :return:
            A dictionary retlist with results
            {'result': <result of the HTTP request>}
        """
        retlist = {}
        res = self.post(self.baseurl + "users", data)
        retlist['result'] = res['response']
        return retlist

    def deluser(self, user):
        retlist = {}
        res = self.delete(self.baseurl + "users/" + user)
        retlist['result'] = res['response']
        return retlist

    def updateuser(self, data):
        """
        Update user data
        :param data:
             A dictionary with user data
        :return:
            A dictionary retlist with results
            {'result': <result of the HTTP request>}
        """
        # ToDo att a check to see if the user exists
        return self.adduser(data)

    def checkuser(self, user):
        """
        Check to see if a user exists
        :param user:
            userid of the user to check for
        :return:
            True if the user exist
            False if the user doesnt exist
        """
        ids = self.get(self.baseurl + "users/" + user)
        if ids['response'] == 200:
            return True
        else:
            return False

    def gettopics(self, boardid):
        """
        Get all topics for a boardid
        :param boardid:
            Boardid to check for topics
        :return:
            A dictionary with results
            {'data':[<topicid1>, <topicid2>]
             'result': <result of the HTTP request>
            }
        """
        retlist = {'data':[]}
        ids = self.get(self.baseurl + "boards/" + boardid + '/topics')
        retlist['result'] = ids['response']
        if 'datalist' in ids:
            for id in ids['datalist']:
                retlist['data'].append(str(id['topicid']))
        return retlist

    def gettopic(self, boardid, topicid):
        """
        Get data for a specific topic id
        :param boardid:
            Board id
        :param topicid:
            Topic id
        :return:
            A dictionary with results
            {'data':[<topic data>]
             'result': <result of the HTTP request>
            }
        """
        retlist = {'data':[]}
        topic = self.get(self.baseurl + 'boards/' + boardid + '/topics/' + topicid)
        retlist['result'] = topic['response']
        if 'datalist' in topic:
            retlist['data'].append(topic['datalist'][0])
        return retlist

    def addtopic(self, boardid, data):
        """
        Add data for a topic
        :param boardid:
            Board id
        :param data:
            A dictionary with user data
        :return:

        """
        retlist = {}
        res = self.post(self.baseurl + "boards/" + boardid + "/topics", data)
        retlist['result'] = res['response']
        return retlist

    def deltopic(self, boardid, topicid):
        """
        Delete a topic
        :param boardid:
            Board id
        :param topicid:
            Topic id to delete
        :return:
            A dictionary with results
            {'result': <result of the HTTP request>}
        """
        retlist = {}
        res = self.delete(self.baseurl + "boards/" + boardid + "/topics/" + topicid)
        retlist['result'] = res['response']
        return retlist

    def getvotes(self, boardid, topicid):
        """
        Get votes for a topic id
        :param boardid:
            Board id
        :param topicid:
            Topic id
        :return:
            A dictionary with results
            {'data':[<voted1>, <voteid2>]
             'result': <result of the HTTP request>
            }
        """
        retlist = {'data':[]}
        vids = self.get(self.baseurl + "boards/" + boardid + '/topics/' + topicid + '/votes')
        retlist['result'] = vids['response']
        if 'datalist' in vids:
            for id in vids['datalist']:
                retlist['data'].append(str(id['voteid']))
        return retlist

    def getvote(self, boardid, topicid, voteid):
        """
        Get data for a specific vote
        :param boardid:
            Board id
        :param topicid:
            Topic id
        :param voteid:
            Vote id
        :return:
            A dictionary retlist with results
            {'data':[<vote data>]
             'result': <result of the HTTP request>
        """
        retlist = {'data': []}
        vote = self.get(self.baseurl + "boards/" + boardid + '/topics/' + topicid + '/votes/' + voteid)
        retlist['result'] = vote['response']
        if 'datalist' in vote:
            retlist['data'].append(vote['datalist'][0])
        return retlist

    def addvote(self, boardid, topicid, data):
        """
        Add a vote to a topic
        :param boardid:
            Board id
        :param topicid:
            Topic Id
        :param data:
            Data about the vote
        :return:
            A dictionary with results
            {'result': <result of the HTTP request>}
        """
        retlist = {}
        res = self.post(self.baseurl + "boards/" + boardid + "/topics/" + topicid + "/votes", data)
        retlist['result'] = res['response']
        return retlist

    def delvote(self, boardid, topicid, user):
        """
        Delete a vote from a topic
        :param boardid:
            Board id
        :param topicid:
             Topic id
        :param user:
            The user doing the delete
        :return:
            A dictionary with results
            {'result': <result of the HTTP request>}
        """
        retlist = {}
        shadow1 = self.getvotes(boardid, topicid)
        for voteid in shadow1['data']:
            shadow2 = self.getvote(boardid, topicid, voteid)
            for vote in shadow2['data']:
                if vote['user'] == user:
                    res = self.delete(self.baseurl + "boards/" + boardid + "/topics/" + topicid + "/votes/" + voteid)
                    retlist['result'] = res['response']
                    return retlist
        retlist['result'] = shadow1['response']
        return retlist

    def getconfig(self):
        """
        Get backend configuration data
        :return:
            A dictionary with backend configuration
            {'data':[<config data data>]
             'result': <result of the HTTP request>
        """
        retlist = {'data': []}
        cfg = self.get(self.baseurl + "config")
        retlist['result'] = cfg['response']
        if 'datalist' in cfg:
            retlist['data'].append(cfg['datalist'])
        return retlist

    def setconfig(self, data):
        retlist = {}
        res = self.post(self.baseurl + "config", data)
        retlist['result'] = res['response']
        return retlist

    def getdbstatus(self):
        retlist = {'data': []}
        cfg = self.get(self.baseurl + "db")
        retlist['result'] = cfg['response']
        if 'datalist' in cfg:
            retlist['data'].append(cfg['datalist'])
        return retlist

    def getbackendstatus(self):
        retlist = {'data': []}
        cfg = self.get(self.baseurl + "backend")
        retlist['result'] = cfg['response']
        if 'datalist' in cfg:
            retlist['data'].append(cfg['datalist'])
        return retlist
