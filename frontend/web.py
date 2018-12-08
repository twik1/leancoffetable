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


def update_session(param):
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']
        if session['username'] == 'admin':
            param['ctrl']['admin'] = 'yes'
        return True
    return False


def sortlist(list):
    if len(list) == 0:
        #Nothing to sort
        return list
    newlist = []
    i = 0
    j = 0
    lowest = list[0]['topicvotes']
    while len(list) > 0:
        for i in range(0, len(list)):
            if list[i]['topicvotes'] <= lowest:
                lowest = list[i]['topicvotes']
                j = i
        newlist.insert(0,list[j])
        del list[j]
        if len(list)>=1:
            lowest = list[0]['topicvotes']
            j = 0
    return newlist

@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    shadow1 = restapi.getboards()
    # ToDO: Check return
    for ids in shadow1['data']:
        shadow2 = restapi.getboard(ids)
        # ToDO: Check return
        param['data'].append(shadow2['data'][0])

    if shadow1['result'] == 0:
        param['ctrl']['errormsg'] = 'No contact with backend'
        return render_template('error', param=param)

    return render_template('index', param=param)


@app.route('/login', methods=['GET', 'POST'])
def login():
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    if request.method == 'POST':
        # Special treatment if user equal admin
        if request.form['user'] == 'admin':
            if request.form['password'] == gcfg.get_cfg('frontend', 'admin_password'):
                session['username'] = request.form['user']
                param['ctrl']['loggedin'] = 'yes'
                return redirect(url_for('index'))
            else:
                param['ctrl']['errormsg'] = 'Faulty user or password'
                return render_template('login', param=param)
        shadow1 = restapi.getuser(request.form['user'])
        if shadow1['result'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error', param=param)
        if not shadow1['result'] == 200:
            param['ctrl']['errormsg'] = 'Faulty user or password'
            return render_template('login', param=param)
        else:
            if pbkdf2_sha256.verify(request.form['password'], shadow1['data'][0]['password']):
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
    update_session(param)
    if request.method == 'POST':
        user = request.form['user']
        name = request.form['name']
        mail = request.form['email']
        password = pbkdf2_sha256.encrypt(request.form['password'], rounds=200000, salt_size=16)
        if restapi.checkuser(user) or user == 'admin':
            param['ctrl']['errormsg'] = 'User already exist'
            return render_template('newuser', param=param)
        data = {'user': user, 'name': name, 'password': password, 'mail': mail}
        shadow1 = restapi.adduser(data)
        if shadow1['result'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error', param=param)
        if shadow1['result'] == 201:
            session['username'] = request.form['user']
            param['ctrl']['loggedin'] = 'yes'
            param['ctrl']['sessionname'] = session['username']
            return redirect(url_for('index', param=param))
    else:
        return render_template('newuser', param=param)


@app.route('/eduser', methods=['GET', 'POST'])
def eduser():
    param = {'data': [], 'ctrl': {}}
    if not update_session(param):
        param['ctrl']['errormsg'] = 'You are not logged in'
        return render_template('error', param=param)

    # Special treatment for admin
    if session['username'] == 'admin':
        if request.method == 'GET':
            param['ctrl']['name'] = 'Not used'
            param['ctrl']['email'] = 'not_used@notused.org'
            return render_template('user', param=param)
        else:
            param['ctrl']['name'] = 'Not used'
            param['ctrl']['email'] = 'not_used@notused.org'
            if request.form['password'] == gcfg.get_cfg('frontend', 'admin_password'):
                newpassword = request.form['newpassword']
                newpassword2 = request.form['newpassword2']
                if len(newpassword) or len(newpassword2):
                    if not newpassword == newpassword2:
                        param['ctrl']['errormsg'] = 'New Password and Repeat New Password doesnt match'
                        return render_template('user', param=param)
                    gcfg.set_cfg('frontend', 'admin_password', newpassword)
                param['ctrl']['okmsg'] = 'Values has been updated'
                return render_template('user', param=param)
            else:
                param['ctrl']['errormsg'] = 'Faulty password'
                return render_template('user', param=param)
    else:
        if request.method == 'GET':
            shadow1 = restapi.getuser(session['username'])
            if shadow1['result'] == 0:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error', param=param)
            param['ctrl']['name'] = shadow1['data'][0]['name']
            param['ctrl']['email'] = shadow1['data'][0]['mail']
            return render_template('user', param=param)
        else:
            name = request.form['name']
            mail = request.form['email']
            newpassword = request.form['newpassword']
            newpassword2 = request.form['newpassword2']
            shadow1 = restapi.getuser(session['username'])
            if shadow1['result'] == 0:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error', param=param)
            param['ctrl']['sessionname'] = session['username']
            param['ctrl']['name'] = name
            param['ctrl']['email'] = mail
            if pbkdf2_sha256.verify(request.form['password'], shadow1['data'][0]['password']):
                if len(newpassword) or len(newpassword2):
                    if not newpassword == newpassword2:
                        param['ctrl']['errormsg'] = 'New Password and Repeat New Password doesnt match'
                        return render_template('user', param=param)
                    password = pbkdf2_sha256.encrypt(newpassword, rounds=200000, salt_size=16)
                else:
                    password = shadow1['data'][0]['password']
                user = session['username']
                data = {'user': user, 'name': name, 'password': password, 'mail': mail}
                shadow1 = restapi.updateuser(data)
                if shadow1['result'] == 0:
                    param['ctrl']['errormsg'] = 'No contact with backend'
                    return render_template('error', param=param)
                param['ctrl']['okmsg'] = 'Values has been updated'
                return render_template('user', param=param)
            else:
                param['ctrl']['errormsg'] = 'Faulty password'
                return render_template('user', param=param)


@app.route('/newboard', methods=['GET', 'POST'])
def newboard():
    param = {'data': [], 'ctrl': {}}
    if update_session(param):
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
            shadow1 = restapi.addboard(data)
            if shadow1['result'] == 0:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error', param=param)
            else:
                return redirect(url_for('index'))
        else:
            return render_template('newboard', param=param)
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to create a board'
        return render_template('error', param=param)


@app.route('/delboard/<boardid>')
def delboard(boardid):
    param = {'data': [], 'ctrl': {}}
    if update_session(param):
        shadow1 = restapi.getboard(boardid)
        if shadow1['result'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error', param=param)
        if not shadow1['result'] == 200:
            param['ctrl']['errormsg'] = 'No such board'
            return render_template('error', param=param)
        if (not shadow1['data'][0]['user'] == session['username']) and (not 'admin' in param['ctrl']):
            param['ctrl']['errormsg'] = 'Can not delete someone else\'s board'
            return render_template('error', param=param)
        else:
            shadow2 = restapi.delboard(boardid)
            if shadow2['result'] == 0:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error', param=param)
            if not shadow2['result'] == 201:
                param['ctrl']['errormsg'] = 'No such board'
                return render_template('error', param=param)
            else:
                return redirect(url_for('index'))
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to delete a board'
        return render_template('error', param=param)


@app.route('/board/<boardid>', methods=['GET'])
def board(boardid):
    param = {'data': [], 'ctrl': {}}
    index = 0 # topic index in data
    update_session(param)
    myboardvotes = 0  # Total number of votes for me of the entire board

    # We need some board data
    shadow1 = restapi.getboard(boardid)
    param['ctrl']['votenum'] = shadow1['data'][0]['votenum']
    param['ctrl']['boardname'] = shadow1['data'][0]['name']
    param['ctrl']['boardid'] = boardid

    shadow1 = restapi.gettopics(boardid)
    # ToDO: Check return
    for topic in shadow1['data']:
        topicvotes = 0  # Total number of votes for each topic
        mytopicvotes = 0  # Total number of of votes for me for each topic
        shadow2 = restapi.gettopic(boardid, topic)
        # ToDO: Check return
        param['data'].append(shadow2['data'][0])
        shadow3 = restapi.getvotes(boardid, topic)
        for voteid in shadow3['data']:
            shadow4 = restapi.getvote(boardid, topic, voteid)
            for vote in shadow4['data']:
                topicvotes += 1
                if 'sessionname' in param['ctrl'].keys():
                    if vote['user'] == param['ctrl']['sessionname']:
                        mytopicvotes += 1
                        myboardvotes += 1
        param['data'][index]['topicvotes'] = topicvotes
        param['data'][index]['mytopicvotes'] = mytopicvotes
        index += 1
    param['ctrl']['myboardvotes'] = myboardvotes
    if shadow1['result'] == 0:
        param['ctrl']['errormsg'] = 'No contact with backend'
        return render_template('error', param=param)
    if request.args.get('sort'):
        tmplist = sortlist(param['data'])
        param['data'] = tmplist
    return render_template('board', param=param)


@app.route('/boards/<boardid>',methods=['GET','POST'])
def newtopic(boardid):
    # ToDo: figure out how boardid is treated?
    param = {'data': [], 'ctrl': {}}
    if update_session(param):
        if request.method == 'POST':
            topicheading = request.form['topicheading']
            topicdesc = request.form['topicdesc']
            boardid = request.form['boardid']
            data = {'heading':topicheading, 'description':topicdesc, 'username':session['username']}
            shadow1 = restapi.addtopic(boardid, data)
            # ToDo: branch on correct values
            if not shadow1['result'] == 0:
                return redirect(url_for('board', boardid=boardid))
            else:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error', param=param)
        else:
            param['boardid'] = boardid
            return render_template('newtopic', param=param)
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to create a topic'
        return render_template('error', param=param)


@app.route('/boards/<boardid>/deltopic/<topicid>', methods=['GET'])
def deltopic(boardid, topicid):
    param = {'data': [], 'ctrl': {}}
    if update_session(param):
        shadow1 = restapi.gettopic(boardid, topicid)
        if shadow1['result'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error', param=param)
        if not shadow1['result'] == 200:
            param['ctrl']['errormsg'] = 'No such topic'
            return render_template('error', param=param)
        if (not shadow1['data'][0]['user'] == session['username']) and (not 'admin' in param['ctrl']):
            param['ctrl']['errormsg'] = 'Can not delete anyone else topic'
            return render_template('error', param=param)
        else:
            shadow1 = restapi.deltopic(boardid, topicid)
            if shadow1['result'] == 0:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error', param=param)
            if not shadow1['result'] == 201:
                param['ctrl']['errormsg'] = 'No such board'
                return render_template('error', param=param)
            else:
                return redirect(url_for('board', boardid=boardid))
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to delete a topic'
        return render_template('error', param=param)


@app.route('/boards/<boardid>/topics/<topicid>/votes', methods=['GET'])
def newvote(boardid, topicid):
    if 'username' in session.keys():
        data = {'user': session['username'], 'topicid': topicid}
        shadow1 = restapi.addvote(boardid, topicid, data)
    return redirect(url_for('board', boardid=boardid))


@app.route('/boards/<boardid>/topics/<topicid>/votes/<voteid>', methods=['GET'])
def delvote(boardid, topicid, voteid):
    if 'username' in session.keys():
        ret = restapi.delvote(boardid, topicid, session['username'])
    return redirect(url_for('board', boardid=boardid))


@app.route('/about', methods=['GET'])
def about():
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    return render_template('about', param=param)


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    global gcfg
    global gqueue
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    if request.method == 'POST':
        # Get all fields and store in cfg and write
        gcfg.set_cfg('frontend', 'backend_host', request.form['backend_host'])
        gcfg.set_cfg('frontend', 'backend_port', request.form['backend_port'])
        restapi.setbaseurl(gcfg.get_cfg('frontend', 'backend_host'), gcfg.get_cfg('frontend', 'backend_port'))
        # If listen address change restart
        listen_address = gcfg.get_cfg('frontend', 'listen_address')
        listen_port = gcfg.get_cfg('frontend', 'listen_port')
        if not listen_address == request.form['listen_address'] or not listen_port == request.form['listen_port']:
            gcfg.set_cfg('frontend', 'listen_address', request.form['listen_address'])
            gcfg.set_cfg('frontend', 'listen_port', request.form['listen_port'])
            gqueue.put('restart')
        return redirect(url_for('setup'))
    else:
        # Check backend status
        # ToDo change to only test backend
        shadow1 = restapi.getdbstatus()
        if shadow1['result'] == 200:
            param['ctrl']['backend_status'] = 'ok'
        else:
            param['ctrl']['backend_status'] = 'fail'

        param['ctrl']['listen_address'] = gcfg.get_cfg('frontend', 'listen_address')
        param['ctrl']['listen_port'] = gcfg.get_cfg('frontend', 'listen_port')
        param['ctrl']['backend_host'] = gcfg.get_cfg('frontend', 'backend_host')
        param['ctrl']['backend_port'] = gcfg.get_cfg('frontend', 'backend_port')

        shadow1 = restapi.getconfig()
        if shadow1['result'] == 200:
            param['data'] = shadow1['data'][0]
        shadow1 = restapi.getdbstatus()
        if shadow1['result'] == 200:
            if shadow1['data'][0]['db_result'] == '0':
                param['ctrl']['db_status'] = 'ok'
            else:
                param['ctrl']['db_status'] = 'fail'
        return render_template('setup', param=param)

@app.route('/backendsetup', methods=['POST'])
def backsetup():
    global gcfg
    param = {'data': [], 'ctrl': {}}
    data = {}
    update_session(param)
    if request.method == 'POST':
        for field, value in request.form.items():
            data[field] = value
        restapi.setconfig(data)
    return redirect(url_for('setup'))


def start_frontend(queue, argd):
    global gqueue
    global gcfg

    gqueue = queue
    gcfg = config.Config('.lct', 'lctfrontend')

    # Frontend listen address and port is taken from start argument
    # If it's not given check config file otherwise use default
    # The rest could be configured through web interface
    if 'addr' in argd.keys():
        gcfg.set_cfg('frontend', 'listen_address', argd['addr'])
    elif not gcfg.get_cfg('frontend', 'listen_address'):
        gcfg.set_cfg('frontend', 'listen_address', "0.0.0.0")
    if 'port' in argd.keys():
        gcfg.set_cfg('frontend', 'listen_port', argd['port'])
    elif not gcfg.get_cfg('frontend', 'listen_address'):
        gcfg.set_cfg('frontend', 'listen_port', '5050')
    if not gcfg.get_cfg('frontend', 'backend_host'):
        gcfg.set_cfg('frontend', 'backend_host', '0.0.0.0')
    backend_host = gcfg.get_cfg('frontend', 'backend_host')
    if not gcfg.get_cfg('frontend', 'backend_port'):
        gcfg.set_cfg('frontend', 'backend_port', '5000')
    if not gcfg.get_cfg('frontend', 'admin_password'):
       gcfg.set_cfg('frontend', 'admin_password', 'admin')
    backend_port = gcfg.get_cfg('frontend', 'backend_port')
    restapi.setbaseurl(backend_host, backend_port)

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

    if args.listen_address:
        frontend_parameter['addr'] = args.listen_address
    if args.listen_port:
        frontend_parameter['port'] = args.listen_port

    daemon = Daemon(start_frontend)
    daemon.start(frontend_parameter)
