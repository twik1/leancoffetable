from flask import Flask, render_template, request, redirect, url_for, session
import rest
from flask_session import Session
from passlib.hash import pbkdf2_sha256
import argparse
from waitress import serve
import config
from multiprocessing import Process, Queue
import subprocess
import time
import sys

app = Flask(__name__)

sess = Session()
restapi = rest.CurlREST()


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


@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    param = {'data': [], 'ctrl': {}}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']
    restapi.getboards(param)
    if param['ctrl']['response'] == 0:
        param['ctrl']['errormsg'] = 'No contact with backend'
        return render_template('error', param=param)

    return render_template('index',param=param)


@app.route('/login', methods=['GET', 'POST'])
def login():
    param = {'data': [], 'ctrl': {}}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']
    if request.method == 'POST':
        ret = restapi.getuser(param, request.form['user'])
        if ret == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        if not ret == 200:
            param['ctrl']['errormsg'] = 'Faulty user or password'
            return render_template('login', param=param)
        else:
            if pbkdf2_sha256.verify(request.form['password'], param['data'][0]['password']):
                session['username'] = request.form['user']
                param['ctrl']['loggedin'] = 'yes'
                return redirect(url_for('index'))
            else:
                param['ctrl']['errormsg'] = 'Faulty user or password'
                return render_template('login', param=param)
    else:
        return render_template('login', param=param)


@app.route('/logout', methods=['GET'])
def logout():
    param = {'data': [], 'ctrl': {}}
    if 'username' in session.keys():
        session.pop('username')
    return render_template('login', param=param)


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    param = {'data': [], 'ctrl': {}}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

    if request.method == 'POST':
        user = request.form['user']
        name = request.form['name']
        mail = request.form['email']
        password = pbkdf2_sha256.encrypt(request.form['password'], rounds=200000, salt_size=16)
        if restapi.checkuser(user):
            param['ctrl']['errormsg'] = 'User already exist'
            return render_template('newuser', param=param)
        data = {'user': user,'name': name, 'password': password, 'mail': mail}
        # ret = restapi.post('http://localhost:5000/lct/api/v1.0/users', data)
        ret = restapi.adduser(data)
        if ret == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error', param=param)
        if ret == 201:
            session['username'] = request.form['user']
            param['ctrl']['loggedin'] = 'yes'
            param['ctrl']['sessionname'] = session['username']
            return redirect(url_for('index', param=param))
    else:
        return render_template('newuser', param=param)


@app.route('/user.html',methods=['GET', 'POST'])
def user():
    param = {}
    param['data'] = []
    param['ctrl'] = {}
    if not 'username' in session.keys():
        param['ctrl']['errormsg'] = 'You are not logged in'
        return render_template('error.html', param=param)
    param['ctrl']['loggedin'] = 'yes'
    param['ctrl']['sessionname'] = session['username']
    if request.method == 'GET':
        ret = restapi.get('http://localhost:5000/lct/api/v1.0/users/'+session['username'])
        if ret['response'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        param['ctrl']['name'] = ret['datalist'][0]['name']
        param['ctrl']['email'] = ret['datalist'][0]['mail']
        return render_template('user.html', param=param)
    else:
        # user = request.form['user']
        name = request.form['name']
        mail = request.form['email']
        newpassword = request.form['newpassword']
        newpassword2 = request.form['newpassword2']
        ret = restapi.get('http://localhost:5000/lct/api/v1.0/users/'+session['username'])
        if ret['response'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        if pbkdf2_sha256.verify(request.form['password'], ret['datalist'][0]['password']):
            if len(newpassword) or len(newpassword2):
                if not newpassword == newpassword2:
                    param['ctrl']['errormsg'] = 'New Password and Repeat New Password doesnt match'
                    return render_template('user.html', param=param)
                password = pbkdf2_sha256.encrypt(newpassword, rounds=200000, salt_size=16)
            else:
                password = ret['datalist'][0]['password']
            user = session['username']
            data = {'user': user, 'name': name, 'password': password, 'mail': mail}
            ret = restapi.post('http://localhost:5000/lct/api/v1.0/users', data)
            if ret['response'] == 0:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error.html', param=param)
            param['ctrl']['sessionname'] = session['username']
            param['ctrl']['name'] = name
            param['ctrl']['email'] = mail
            param['ctrl']['okmsg'] = 'Values has been updated'
            return render_template('user.html', param=param)
        else:
            param['ctrl']['errormsg'] = 'Faulty password'
            return render_template('user.html', param=param)


@app.route('/newboard', methods=['GET', 'POST'])
def newboard():
    param = {}
    param['data'] = []
    param['ctrl'] = {}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

    if request.method == 'POST':
        username = request.form['username']
        boardname = request.form['boardname']
        startdate = request.form['startdate']
        votenum = request.form['votenum']
        if votenum == 'Unlimited':
            votenum = '0'
        if startdate == '':
            startdate = '1970-01-01T00:00'
        data = {'username':username, 'boardname':boardname, 'startdate':startdate, 'votenum':votenum}
        if restapi.post('http://localhost:5000/lct/api/v1.0/boards', data):
            return redirect(url_for('index'))
        else:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
    else:
        return render_template('newboard.html', param=param)


@app.route('/delboard/<boardid>')
def delboard(boardid):
    param = {}
    param ['ctrl'] ={}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

    if 'username' in session.keys():
        ret = restapi.get('http://localhost:5000/lct/api/v1.0/boards/'+boardid)
        if ret['response'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        if not ret['response'] == 200:
            param['ctrl']['errormsg'] = 'No such board'
            return render_template('login.html', param=param)
        if not ret['datalist'][0]['user'] == session['username']:
            param['ctrl']['errormsg'] = 'Can not delete anyone else board'
            return render_template('error.html', param=param)
        else:
            ret = restapi.delete('http://localhost:5000/lct/api/v1.0/boards/' + boardid)
            if ret['response'] == 0:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error.html', param=param)
            if not ret['response'] == 201:
                param['ctrl']['errormsg'] = 'No such board'
                return render_template('error.html', param=param)
            else:
                return redirect(url_for('index'))
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to delete a board'
        return render_template('error.html', param=param)


@app.route('/board/<boardid>')
def board(boardid):
    param = {}
    param['ctrl'] ={}
    param['ctrl']['boardid'] = boardid
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']
    param = restapi.gettopics(boardid, param)
    if param['ctrl']['response'] == 0:
        param['ctrl']['errormsg'] = 'No contact with backend'
        return render_template('error.html', param=param)
    return render_template('board.html', param=param)


@app.route('/boards/<boardid>',methods=['GET','POST'])
def newtopic(boardid):
    param = {}
    param ['ctrl'] ={}
    param['boardid'] = boardid
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

    if request.method == 'POST':
        topicheading = request.form['topicheading']
        topicdesc = request.form['topicdesc']
        boardid = request.form['boardid']
        data = {'heading':topicheading, 'description':topicdesc, 'username':session['username']}
        if restapi.post('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics', data):
            return redirect(url_for('board', boardid=boardid))
        else:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
    else:
        return render_template('newtopic.html', param=param)


@app.route('/boards/<boardid>/deltopic/<topicid>', methods=['GET'])
def deltopic(boardid, topicid):
    param = {}
    param['ctrl'] = {}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

        ret = restapi.get('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics/'+topicid)
        if ret['response'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        if not ret['response'] == 200:
            param['ctrl']['errormsg'] = 'No such topic'
            return render_template('error.html', param=param)
        if not ret['datalist'][0]['user'] == session['username']:
            param['ctrl']['errormsg'] = 'Can not delete anyone else topic'
            return render_template('error.html', param=param)
        else:
            ret = restapi.delete('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics/'+topicid)
            if ret['response'] == 0:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error.html', param=param)
            if not ret['response'] == 201:
                param['ctrl']['errormsg'] = 'No such board'
                return render_template('error.html', param=param)
            else:
                return redirect(url_for('board', boardid=boardid))
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to delete a board'
        return render_template('error.html', param=param)


@app.route('/boards/<boardid>/topics/<topicid>/votes', methods=['GET'])
def newvote(boardid, topicid):
    if 'username' in session.keys():
        data = {'user': session['username'], 'topicid': topicid}
        ret = restapi.post('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics/'+topicid+'/votes', data)
    return redirect(url_for('board', boardid=boardid))


@app.route('/boards/<boardid>/topics/<topicid>/votes/<voteid>', methods=['GET'])
def delvote(boardid, topicid, voteid):
    if 'username' in session.keys():
        ret = restapi.delvote(boardid, topicid, voteid, session['username'])
        # ret = restapi.delete('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics/'+topicid+'/votes/'+voteid)
    return redirect(url_for('board', boardid=boardid))


@app.route('/about.html', methods=['GET'])
def about():
    param = {}
    param['ctrl'] = {}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']
    return render_template('about.html', param=param)


@app.route('/setup.html', methods=['GET'])
def setup():
    param = {}
    param['ctrl'] = {}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']
    param = restapi.getconfig(param)
    if param['ctrl']['response'] == 0:
        param['ctrl']['errormsg'] = 'No contact with backend'
        return render_template('error.html', param=param)
    return render_template('setup.html', param=param)


def start_frontend(queue, argd):
    global gqueue
    global gcfg

    gqueue = queue
    gcfg = config.Config('.lct', 'lctfrontend')

    # Frontend listen address and port is taken from start argument
    # The rest could be configured through web interface
    gcfg.set_cfg('frontend', 'listen_address', argd['addr'])
    gcfg.set_cfg('frontend', 'listen_port', argd['port'])
    gcfg.set_cfg('frontend', 'backend_host', '0.0.0.0')
    gcfg.set_cfg('frontend', 'backend_port', '5000')

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)

    serve(app, listen=gcfg.get_cfg('frontend', 'listen_address') + ':' + gcfg.get_cfg('frontend', 'listen_port'))


if __name__ == '__main__':
    frontend_parameter = {}
    parser = argparse.ArgumentParser(description='Lean Coffe Table frontend')
    parser.add_argument('-l', '--listen_address', help='Frontend listen address', required=False)
    parser.add_argument('-p', '--listen_port', help='Frontend listen port', required=False)
    args = parser.parse_args()

    if not args.listen_address:
        frontend_parameter['addr'] = '0.0.0.0'
    else:
        frontend_parameter['addr'] = args.listen_address
    if not args.listen_port:
        frontend_parameter['port'] = '5050'
    else:
        frontend_parameter['port'] = args.listen_port

    daemon = Daemon(start_frontend)
    daemon.start(frontend_parameter)
