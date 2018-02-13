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
                response.update(ret.json()[0])
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



    def delete(self, url, param):
        try:
            ret = requests.put(url, headers=self.headers, data=json.dumps(param))
            return ret
        except requests.exceptions.RequestException as e:
            return None

    def getboards(self):
        boardlist = []
        ids = self.get(self.baseurl+"boards")
        for id in ids:
            board = self.get(self.baseurl+'boards/'+str(id['boardid']))
            print(board)