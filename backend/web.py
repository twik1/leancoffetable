#!flask/bin/python
from flask import Flask, abort, request, jsonify, make_response
import mysqldb
import json
import datetime


app = Flask(__name__)


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


##################################################

@app.route('/lct/api/v1.0/users', methods=['GET'])
def get_users():
    dbuserlist = dbconnect.get_users()
    return jsonify(dbuserlist)


@app.route('/lct/api/v1.0/users', methods=['POST'])
def add_user():
    if not check_result(['user','password']):
        abort(make_response(jsonify(message="Missing parameter"), 404))
    user = {
        'user': request.json['user'],
        'name': request.json.get('name', ""),
        'password': request.json['password']
    }
    dbconnect.add_user(user)
    return jsonify({'user': request.json['user']}), 201


@app.route('/lct/api/v1.0/users/<user>', methods=['GET'])
def get_user(user):
    dbuser = dbconnect.get_user(user)
    if not len(dbuser):
        abort(make_response(jsonify(message="No such user"), 404))
    return jsonify(dbuser)


@app.route('/lct/api/v1.0/users/<user>', methods=['PUT'])
def update_user(user):
    if not check_result(['password']):
        abort(make_response(jsonify(message="Missing parameter"), 404))
    if not dbconnect.check_user(user):
        abort(make_response(jsonify(message="No such user"), 404))
    user = {
        'user': user,
        'name': request.json.get('name', ""),
        'password': request.json['password']
    }
    dbconnect.add_user(user)
    return jsonify({'user': user}), 201


@app.route('/lct/api/v1.0/users/<user>', methods=['DELETE'])
def delete_user(user):
    if not dbconnect.check_user(user):
        abort(make_response(jsonify(message="No such user"), 404))
    dbconnect.del_user(user)
    return jsonify({'user': user}), 201

###########################################################

@app.route('/lct/api/v1.0/boards', methods=['GET'])
def get_boards():
    dbboardlist = dbconnect.get_boards()
    return jsonify(dbboardlist)


@app.route('/lct/api/v1.0/boards', methods=['POST'])
def add_board():
    if not check_result(['boardname','username','startdate']):
        abort(make_response(jsonify(message="Missing parameter"), 404))
    if not dbconnect.check_user(request.json['username']):
        abort(make_response(jsonify(message="No such user"), 404))
    startdate = conv_startdate(request.json['startdate'])

    board = {
        'username': request.json['username'],
        'boardname': request.json['boardname'],
        'startdate': startdate,
        }
    dbconnect.add_board(board)
    # ToDo: return boardid
    return jsonify(board), 201


@app.route('/lct/api/v1.0/boards/<boardid>', methods=['GET'])
def get_board(boardid):
    dbboard = dbconnect.get_board(boardid)
    if not len(dbboard):
        abort(make_response(jsonify(message="No such board"), 404))
    return jsonify(dbboard)


@app.route('/lct/api/v1.0/boards/<boardid>', methods=['PUT'])
def update_board(boardid):
    if not check_result(['boardname','username']):
        abort(make_response(jsonify(message="Missing parameter"), 404))
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    if not dbconnect.check_user(request.json['user']):
        abort(make_response(jsonify(message="No such user"), 404))
    board = {
        'boardname': request.json['boardname'],
        'username': request.json['username'],
        'startdate': request.json['startdate'],
        'boardid': boardid,
    }
    dbconnect.update_board(board)
    # ToDo: return boardid
    return jsonify(board), 201


@app.route('/lct/api/v1.0/boards/<boardid>', methods=['DELETE'])
def delete_board(boardid):
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    dbconnect.del_board(boardid)
    return jsonify({'boardid': boardid}), 201

###################################################################


@app.route('/lct/api/v1.0/boards/<boardid>/topics', methods=['GET'])
def get_topics(boardid):
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    dbtopiclist = dbconnect.get_topics(boardid)
    return jsonify(dbtopiclist)


@app.route('/lct/api/v1.0/boards/<boardid>/topics', methods=['POST'])
def add_topic(boardid):
    if not check_result(['heading','description']):
        abort(make_response(jsonify(message="Missing parameter"), 404))
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    topic = {
        'heading': request.json['heading'],
        'description': request.json['description'],
        'boardid': boardid,
        }
    dbconnect.add_topic(topic)
    # ToDo: return topicid
    return jsonify(topic), 201


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>', methods=['GET'])
def get_topic(boardid, topicid):
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    dbtopic = dbconnect.get_topic(topicid)
    if not len(dbtopic):
        abort(make_response(jsonify(message="No such topic"), 404))
    return jsonify(dbtopic)


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>', methods=['PUT'])
def update_topic(boardid, topicid):
    if not check_result(['heading','description']):
        abort(make_response(jsonify(message="Missing parameter"), 404))
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    if not dbconnect.check_topic(topicid):
        abort(make_response(jsonify(message="No such topic"), 404))
    topic = {
        'heading': request.json['heading'],
        'description': request.json['description'],
        'topicid': topicid,
        'boardid': boardid,
    }
    dbconnect.update_topic(topic)
    # ToDo: return topicid
    return jsonify(topic), 201

@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>', methods=['DELETE'])
def delete_topic(boardid, topicid):
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    if not dbconnect.check_topic(topicid):
        abort(make_response(jsonify(message="No such topic"), 404))
    dbconnect.del_topic(topicid)
    return jsonify({'topicid': topicid}), 201

#######################################################


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>/votes', methods=['GET'])
def get_votes(boardid, topicid):
    if not dbconnect.check_board(boardid):
        abort(400)
    if not dbconnect.check_topic(topicid):
        abort(400)
    dbvotelist = dbconnect.get_votes(boardid,topicid)
    return json.dumps(dbvotelist)


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>/votes', methods=['POST'])
def add_vote(boardid, topicid):
    if not check_result(['user']):
        abort(make_response(jsonify(message="Missing parameter"), 404))
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    if not dbconnect.check_topic(topicid):
        abort(make_response(jsonify(message="No such topic"), 404))
    vote = {
        'user': request.json['user'],
        'topicid': topicid,
        }
    dbconnect.add_vote(vote)
    # ToDo: return topicid
    return jsonify(vote), 201


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>/votes/<voteid>', methods=['GET'])
def get_vote(boardid, topicid, voteid):
    if not dbconnect.check_board(boardid):
        abort(400)
    if not dbconnect.check_topic(topicid):
        abort(400)
    dbvote = dbconnect.get_vote(topicid,voteid)
    if not len(dbvote):
        abort(make_response(jsonify(message="No such vote"), 404))
    return jsonify(dbvote)


@app.route('/lct/api/v1.0/boards/<boardid>/topics/<topicid>/votes/<voteid>', methods=['DELETE'])
def delete_vote(boardid, topicid, voteid):
    if not dbconnect.check_board(boardid):
        abort(make_response(jsonify(message="No such board"), 404))
    if not dbconnect.check_topic(topicid):
        abort(make_response(jsonify(message="No such topic"), 404))
    dbconnect.del_vote(voteid)
    return jsonify({'voteid': voteid}), 201


if __name__ == '__main__':
    dbconnect = mysqldb.DBMySQL('127.0.0.1', 'lctusr', 'lctpwd', 'lctdb')
    app.run(debug=True)
