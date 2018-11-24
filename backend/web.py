#!flask/bin/python
from flask import Flask, abort, request, jsonify, make_response
from multiprocessing import Process, Queue
from waitress import serve
import mysqldb
import json
import datetime
import config
import time
import sys
import subprocess
import argparse


LCTBVER = '0.0.1'

app = Flask(__name__)


class Daemon:
    def __init__(self, method):
        self.q = Queue()
        self.method = method

    def start(self, argsd):
        self.p = Process(target=self.method, args=[self.q, argsd])
        self.p.start()
        while True:
            if self.q.empty():  # sleep on queue?
                time.sleep(1)
            else:
                msg = self.q.get()
                break
        self.p.terminate()

        if msg == 'restart':
            args = [sys.executable] + [sys.argv[0]]
            subprocess.call(args)


def check_result(parameterlist):
    if not request.is_json:
        return False
    parameters = request.get_json()
    for parameter in parameterlist:
        if not parameter in parameters:
            return False
    return True


def conv_startdate(startdate):
    date_processing = startdate.replace('T', '-').replace(':', '-').split('-')
    date_processing = [int(v) for v in date_processing]
    return datetime.datetime(*date_processing)


def gabort(msg, resp):
    dbconnect.disconn()
    abort(make_response(jsonify(message=msg), resp))


##################################################

@app.route('/lct/api/v1.0/users', methods=['GET'])
def get_users():
    dbconnect.conn()
    dbuserlist = dbconnect.get_users()
    dbconnect.disconn()
    return jsonify(dbuserlist)


@app.route('/lct/api/v1.0/users', methods=['POST'])
def add_user():
    dbconnect.conn()
    if not check_result(['user', 'password']):
        gabort("Missing parameter", 404)
    user = {
        'user': request.json['user'],
        'name': request.json.get('name', ""),
        'password': request.json['password'],
        'mail': request.json['mail']
    }
    dbconnect.add_user(user)
    dbconnect.disconn()
    return jsonify({'user': request.json['user']}), 201


@app.route('/lct/api/v1.0/users/<user>', methods=['GET'])
def get_user(user):
    dbconnect.conn()
    dbuser = dbconnect.get_user(user)
    if not len(dbuser):
        gabort("No such user", 404)
    dbconnect.disconn()
    return jsonify(dbuser)


@app.route('/lct/api/v1.0/users/<user>', methods=['PUT'])
def update_user(user):
    dbconnect.conn()
    if not check_result(['password', 'mail']):
        gabort("Missing parameter", 404)
    if not dbconnect.check_user(user):
        gabort("No such user", 404)
    user = {
        'user': user,
        'name': request.json.get('name', ""),
        'password': request.json['password'],
        'mail': request.json['mail']
    }
    dbconnect.add_user(user)
    dbconnect.disconn()
    return jsonify({'user': user}), 201


@app.route('/lct/api/v1.0/users/<user>', methods=['DELETE'])
def delete_user(user):
    dbconnect.conn()
    if not dbconnect.check_user(user):
        gabort("No such user", 404)
    dbconnect.del_user(user)
    dbconnect.disconn()
    return jsonify({'user': user}), 201

###########################################################


@app.route('/lct/api/v1.0/boards', methods=['GET'])
def get_boards():
    dbconnect.conn()
    dbboardlist = dbconnect.get_boards()
    dbconnect.disconn()
    return jsonify(dbboardlist)


@app.route('/lct/api/v1.0/boards', methods=['POST'])
def add_board():
    dbconnect.conn()
    if not check_result(['boardname', 'username', 'startdate', 'votenum']):
        gabort("Missing parameter", 404)
    if not dbconnect.check_user(request.json['username']):
        gabort("No such user", 404)
    startdate = conv_startdate(request.json['startdate'])

    board = {
        'username': request.json['username'],
        'boardname': request.json['boardname'],
        'startdate': startdate,
        'votenum': request.json['votenum']
        }
    # ToDo: check votenum 0,1,3,5,10
    dbconnect.add_board(board)
    dbconnect.disconn()
    # ToDo: return boardid
    return jsonify(board), 201


@app.route('/lct/api/v1.0/boards/<boardid>', methods=['GET'])
def get_board(boardid):
    dbconnect.conn()
    dbboard = dbconnect.get_board(boardid)
    if not len(dbboard):
        gabort("No such board", 404)
    return jsonify(dbboard)


@app.route('/lct/api/v1.0/boards/<boardid>', methods=['PUT'])
def update_board(boardid):
    dbconnect.conn()
    if not check_result(['boardname', 'username', 'startdate', 'votenum']):
        gabort("Missing parameter", 404)
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    if not dbconnect.check_user(request.json['username']):
        gabort("No such user", 404)
    startdate = conv_startdate(request.json['startdate'])
    board = {
        'username': request.json['username'],
        'boardname': request.json['boardname'],
        'startdate': startdate,
        'votenum': request.json['votenum'],
        'boardid': boardid
    }
    dbconnect.update_board(board)
    dbconnect.disconn()
    # ToDo: return boardid
    return jsonify(board), 201


@app.route('/lct/api/v1.0/boards/<boardid>', methods=['DELETE'])
def delete_board(boardid):
    dbconnect.conn()
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    dbconnect.del_board(boardid)
    dbconnect.disconn()
    return jsonify({'boardid': boardid}), 201

###################################################################


@app.route('/lct/api/v1.0/boards/<boardid>/topics', methods=['GET'])
def get_topics(boardid):
    dbconnect.conn()
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    dbtopiclist = dbconnect.get_topics(boardid)
    dbconnect.disconn()
    return jsonify(dbtopiclist)


@app.route('/lct/api/v1.0/boards/<boardid>/topics', methods=['POST'])
def add_topic(boardid):
    dbconnect.conn()
    if not check_result(['heading', 'description', 'username']):
        gabort("Missing parameter", 404)
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    topic = {
        'heading': request.json['heading'],
        'description': request.json['description'],
        'username': request.json['username'],
        'boardid': boardid,
        }
    dbconnect.add_topic(topic)
    dbconnect.disconn()
    # ToDo: return topicid
    return jsonify(topic), 201


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>', methods=['GET'])
def get_topic(boardid, topicid):
    dbconnect.conn()
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    dbtopic = dbconnect.get_topic(topicid)
    if not len(dbtopic):
        gabort("No such topic", 404)
    dbconnect.disconn()
    return jsonify(dbtopic)


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>', methods=['PUT'])
def update_topic(boardid, topicid):
    dbconnect.conn()
    if not check_result(['heading', 'description', 'username']):
        gabort("Missing parameter", 404)
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    if not dbconnect.check_topic(topicid):
        gabort("No such topic", 404)
    topic = {
        'heading': request.json['heading'],
        'description': request.json['description'],
        'username': request.json['username'],
        'topicid': topicid,
        'boardid': boardid,
    }
    dbconnect.update_topic(topic)
    dbconnect.disconn()
    # ToDo: only owning user can update
    # ToDo: return topicid
    return jsonify(topic), 201


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>', methods=['DELETE'])
def delete_topic(boardid, topicid):
    dbconnect.conn()
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    if not dbconnect.check_topic(topicid):
        gabort("No such topic", 404)
    dbconnect.del_topic(topicid)
    dbconnect.disconn()
    return jsonify({'topicid': topicid}), 201

#######################################################


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>/votes', methods=['GET'])
def get_votes(boardid, topicid):
    dbconnect.conn()
    if not dbconnect.check_board(boardid):
        gabort("", 400)
    if not dbconnect.check_topic(topicid):
        gabort("", 400)
    dbvotelist = dbconnect.get_votes(boardid, topicid)
    dbconnect.disconn()
    return json.dumps(dbvotelist)


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>/votes', methods=['POST'])
def add_vote(boardid, topicid):
    dbconnect.conn()
    if not check_result(['user']):
        gabort("Missing parameter", 404)
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    if not dbconnect.check_topic(topicid):
        gabort("No such topic", 404)
    vote = {
        'user': request.json['user'],
        'topicid': topicid,
        }
    dbconnect.add_vote(vote)
    dbconnect.disconn()
    # ToDo: return topicid
    return jsonify(vote), 201


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>/votes/<voteid>', methods=['GET'])
def get_vote(boardid, topicid, voteid):
    dbconnect.conn()
    if not dbconnect.check_board(boardid):
        gabort("", 400)
    if not dbconnect.check_topic(topicid):
        gabort("", 400)
    dbvote = dbconnect.get_vote(topicid, voteid)
    if not len(dbvote):
        gabort("No such vote", 404)
    dbconnect.disconn()
    return jsonify(dbvote)


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>/votes/<voteid>', methods=['DELETE'])
def delete_vote(boardid, topicid, voteid):
    dbconnect.conn()
    if not dbconnect.check_board(boardid):
        gabort("No such board", 404)
    if not dbconnect.check_topic(topicid):
        gabort("No such topic", 404)
    dbconnect.del_vote(voteid)
    dbconnect.disconn()
    return jsonify({'voteid': voteid}), 201


@app.route('/lct/api/v1.0/config', methods=['POST'])
def set_config():
    global gqueue
    gcfg.set_cfg('backend', 'lct_b_ver', request.json['lct_b_ver'])
    # Make choices depending on the version

    db_host = request.json['db_host']
    db_usr = request.json['db_usr']
    db_pwd = request.json['db_pwd']
    db_name = request.json['db_name']
    gcfg.set_cfg('backend', 'db_host', db_host)
    gcfg.set_cfg('backend', 'db_usr', db_usr)
    gcfg.set_cfg('backend', 'db_pwd', db_pwd)
    gcfg.set_cfg('backend', 'db_name', db_name)
    dbconnect.set_param(db_host, db_usr, db_pwd, db_name)
    # db_res = dbconnect.test_connection()

    if not gcfg.get_cfg('backend', 'listen_address') ==  request.json['listen_address'] or \
            not gcfg.get_cfg('backend', 'listen_port') == request.json['listen_port']:
        gcfg.set_cfg('backend', 'listen_address', request.json['listen_address'])
        gcfg.set_cfg('backend', 'listen_port', request.json['listen_port'])
        gqueue.put('restart')

    return jsonify('success'), 201


@app.route('/lct/api/v1.0/config', methods=['GET'])
def get_config():
    global gcfg
    cfgstore = {'Database host':{'db_host': gcfg.get_cfg('backend', 'db_host')},
                'Database username':{'db_usr': gcfg.get_cfg('backend', 'db_usr')},
                'Database password':{'db_pwd': gcfg.get_cfg('backend', 'db_pwd')},
                'Database name':{'db_name': gcfg.get_cfg('backend', 'db_name')},
                'Backend listen address':{'listen_address': gcfg.get_cfg('backend', 'listen_address')},
                'Backend listen port':{'listen_port': gcfg.get_cfg('backend', 'listen_port')},
                'Backend version':{'lct_b_ver': gcfg.get_cfg('backend', 'lct_b_ver')},
                }
    return jsonify(cfgstore)


@app.route('/lct/api/v1.0/db', methods=['GET'])
def check_db():
    #res = dbconnect.conn()
    ret = dbconnect.test_connection()
    #dbconnect.disconn()

    return jsonify({'db_result':str(ret)})


@app.route('/lct/api/v1.0/backend', methods=['GET'])
def check_backend():
    return jsonify({'backend_result':'ok'})


def start_backend(queue, argd):
    global gqueue
    global gcfg
    global dbconnect

    gqueue = queue
    gcfg = config.Config('.lct', 'lctbackend')

    # Check version of 'old' lct
    # Do we need to upgrade/convert anything
    if not gcfg.get_cfg('backend', 'lct_b_ver') == LCTBVER:
        pass
    gcfg.set_cfg('backend', 'lct_b_ver', LCTBVER)

    # Backend listen address and port is taken from start argument
    # The rest could be configured through web interface
    if 'addr' in argd.keys():
        gcfg.set_cfg('backend', 'listen_address', argd['addr'])
    elif not gcfg.get_cfg('backend', 'listen_address'):
        gcfg.set_cfg('backend', 'listen_address', "0.0.0.0")
    if 'port' in argd.keys():
        gcfg.set_cfg('backend', 'listen_port', argd['port'])
    elif not gcfg.get_cfg('backend', 'listen_address'):
        gcfg.set_cfg('backend', 'listen_port', '5050')

    if not gcfg.get_cfg('backend', 'db_host'):
        gcfg.set_cfg('backend', 'db_host', '127.0.0.1')
    db_host = gcfg.get_cfg('frontend', 'backend_host')
    if not gcfg.get_cfg('backend', 'db_usr'):
        gcfg.set_cfg('backend', 'db_usr', 'lctusr')
    db_usr = gcfg.get_cfg('backend', 'db_usr')
    if not gcfg.get_cfg('backend', 'db_pwd'):
        gcfg.set_cfg('backend', 'db_pwd', 'lctpwd')
    db_pwd = gcfg.get_cfg('backend', 'db_pwd')
    if not gcfg.get_cfg('backend', 'db_name'):
        gcfg.set_cfg('backend', 'db_name', 'lctdb')
    db_name = gcfg.get_cfg('backend', 'db_name')

    dbconnect = mysqldb.DBMySQL(db_host, db_usr, db_pwd, db_name)
    # res = dbconnect.test_connection()

    serve(app, listen=gcfg.get_cfg('backend', 'listen_address') + ':' + gcfg.get_cfg('backend', 'listen_port'))


if __name__ == '__main__':
    backend_parameter = {}
    parser = argparse.ArgumentParser(description='Lean Coffe Table backend')
    parser.add_argument('-l', '--listen_address', help='Backend listen address', required=False)
    parser.add_argument('-p', '--listen_port', help='Backend listen port', required=False)
    args = parser.parse_args()

    if args.listen_address:
        backend_parameter['addr'] = args.listen_address
    if args.listen_port:
        backend_parameter['port'] = args.listen_port

    daemon = Daemon(start_backend)
    daemon.start(backend_parameter)
