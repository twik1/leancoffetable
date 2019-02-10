from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
import rest
from flask_session import Session
from passlib.hash import pbkdf2_sha256
import argparse
#from waitress import serve
from multiprocessing import Process, Queue
import subprocess
import time
import sys
import random
import hashlist
import smtp
sys.path.insert(0, '../backend')
import config

CONST_LCTVER = '0.9.1'

#app = Flask(__name__)

#sess = Session()
#restapi = rest.CurlREST()

tapp = Blueprint('tapp', __name__)

#class Daemon:
#    def __init__(self, method):
#        self.q = Queue()
#        self.method = method

#    def start(self, argsd):
#        self.p = Process(target=self.method, args=[self.q, argsd])
#        self.p.start()
#        while True:
#            if self.q.empty():  # sleep on queue?
#                time.sleep(1)
#            else:
#                msg = self.q.get()
#                break
#        self.p.terminate()
#
#        if msg == 'restart':
#            args = [sys.executable] + [sys.argv[0]]
#            subprocess.call(args)


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

def find_user(mail):
    shadow1 = restapi.getusers()
    for user in shadow1['data']:
        shadow2 = restapi.getuser(user)
        if shadow2['data'][0]['mail'] == mail:
            return user
    return False


@tapp.route('/index', methods=['GET'])
@tapp.route('/', methods=['GET'])
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


@tapp.route('/login', methods=['GET', 'POST'])
def login():
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    if request.method == 'POST':
        # Special treatment if user equal admin
        if request.form['user'] == 'admin':
            if request.form['password'] == gcfg.get_cfg('frontend', 'admin_password'):
                session['username'] = request.form['user']
                param['ctrl']['loggedin'] = 'yes'
                return redirect(url_for('.index'))
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
                return redirect(url_for('.index'))
            else:
                param['ctrl']['errormsg'] = 'Faulty user or password'
                return render_template('login', param=param)
    else:
        return render_template('login', param=param)


@tapp.route('/logout', methods=['GET'])
def logout():
    param = {'data': [], 'ctrl': {}}
    if 'username' in session.keys():
        session.pop('username')
    return render_template('login', param=param)


@tapp.route('/newuser', methods=['GET', 'POST'])
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
            return redirect(url_for('.index', param=param))
    else:
        return render_template('newuser', param=param)


@tapp.route('/eduser', methods=['GET', 'POST'])
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


@tapp.route('/newboard', methods=['GET', 'POST'])
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
                return redirect(url_for('.index'))
        else:
            return render_template('newboard', param=param)
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to create a board'
        return render_template('error', param=param)


@tapp.route('/delboard/<boardid>')
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
                return redirect(url_for('.index'))
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to delete a board'
        return render_template('error', param=param)


@tapp.route('/board/<boardid>', methods=['GET'])
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


@tapp.route('/boards/<boardid>',methods=['GET','POST'])
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
                return redirect(url_for('.board', boardid=boardid))
            else:
                param['ctrl']['errormsg'] = 'No contact with backend'
                return render_template('error', param=param)
        else:
            param['boardid'] = boardid
            return render_template('newtopic', param=param)
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to create a topic'
        return render_template('error', param=param)


@tapp.route('/boards/<boardid>/deltopic/<topicid>', methods=['GET'])
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
                return redirect(url_for('.board', boardid=boardid))
    else:
        param['ctrl']['errormsg'] = 'You need to be logged in to delete a topic'
        return render_template('error', param=param)


@tapp.route('/boards/<boardid>/topics/<topicid>/votes', methods=['GET'])
def newvote(boardid, topicid):
    if 'username' in session.keys():
        data = {'user': session['username'], 'topicid': topicid}
        shadow1 = restapi.addvote(boardid, topicid, data)
    return redirect(url_for('.board', boardid=boardid))


@tapp.route('/boards/<boardid>/topics/<topicid>/votes/<voteid>', methods=['GET'])
def delvote(boardid, topicid, voteid):
    if 'username' in session.keys():
        ret = restapi.delvote(boardid, topicid, session['username'])
    return redirect(url_for('.board', boardid=boardid))


@tapp.route('/about', methods=['GET'])
def about():
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    param['ctrl']['ver'] = CONST_LCTVER
    return render_template('about', param=param)


@tapp.route('/users', methods=['GET', 'POST'])
def users():
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    if not 'admin' in param['ctrl']:
        param['ctrl']['errormsg'] = 'You need to be admin to manage users'
        return render_template('error', param=param)
    if request.method == 'POST':
        for user, value in request.form.items():
            shadow1 = restapi.deluser(user)
        return redirect(url_for('.users'))
    else:
        shadow1 = restapi.getusers()
        if shadow1['result'] == 0:
            param['ctrl']['errormsg'] = 'No contact with backend'
            return render_template('error', param=param)
        index = 0
        for user in shadow1['data']:
            shadow2 = restapi.getuser(user)
            # if result differ from success go error
            usr = { 'mail':shadow2['data'][0]['mail'], 'name':shadow2['data'][0]['name'],
                    'user':shadow2['data'][0]['user'], 'index':index}
            param['data'].append(usr)
            index+=1
        return render_template('users', param=param)


@tapp.route('/setup', methods=['GET', 'POST'])
def setup():
    global gcfg
    global gqueue
    global mail

    param = {'data': [], 'ctrl': {}}
    update_session(param)
    if not 'admin' in param['ctrl']:
        param['ctrl']['errormsg'] = 'You need to be admin use setup'
        return render_template('error', param=param)
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
            gcfg.set_cfg('frontend', 'base_url', request.form['base_url'])
            gqueue.put('restart')
        return redirect(url_for('.setup'))
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

        config = mail.get_config()
        if gcfg.get_cfg('frontend', 'base_url'):
            config['LCT Base URL'] = {'base_url': gcfg.get_cfg('frontend', 'base_url')}
        else:
            config['LCT Base URL'] = {'base_url': ""}
        param['mail'] = config
        if mail.test_conn():
            param['ctrl']['mail_status'] = 'fail'
        else:
            param['ctrl']['mail_status'] = 'ok'
        param['ctrl']['base_url'] = gcfg.get_cfg('frontend', 'base_url')
        return render_template('setup', param=param)


@tapp.route('/backendsetup', methods=['POST'])
def backsetup():
    global gcfg
    param = {'data': [], 'ctrl': {}}
    data = {}
    update_session(param)
    if request.method == 'POST':
        for field, value in request.form.items():
            data[field] = value
        restapi.setconfig(data)
    return redirect(url_for('.setup'))


@tapp.route('/mailsetup', methods=['POST'])
def mailsetup():
    global gcfg
    global mail
    param = {'data': [], 'ctrl': {}}
    data = {}
    update_session(param)
    if request.method == 'POST':
        for field, value in request.form.items():
            data[field] = value
            if not value == "":
                gcfg.set_cfg('frontend', field, value)
        mail.set_min_config(data)

    return redirect(url_for('.setup'))


# check lct_base_usr for exist and sanity
@tapp.route('/recover', methods=['GET', 'POST'])
def recover():
    global hashlist
    global mail
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    if request.method == 'POST':
        if not gcfg.get_cfg('frontend', 'base_url'):
            param['ctrl']['errormsg'] = 'The base URL is not set, let your admin know!'
            return render_template('error', param=param)
        param['ctrl']['infomsg'] = 'If you have an account a recovery link has been sent to your email address'
        lct_url = gcfg.get_cfg('frontend', 'base_url')
        mailto = request.form['email']
        user = find_user(mailto)
        if not user:
            return render_template('recover', param=param)
        hash = hashlist.create(mailto, user, 1)
        mail.send(mailto, "LCT password reset",
                  "Follow link to reset password for LCT: {}/reset?lnk={}".format(lct_url,hash))
        return render_template('recover', param=param)
    else:
        return render_template('recover', param=param)


@tapp.route('/reset', methods=['GET', 'POST'])
def reset():
    global hashlist
    param = {'data': [], 'ctrl': {}}
    update_session(param)
    if request.method == 'GET':
        hash = request.args.get('lnk')
        if hashlist.checkhash(hash):
            param['ctrl']['hash'] = hash
            return render_template('reset', param=param)
        else:
            param['ctrl']['errormsg'] = 'No active password reset'
            return render_template('error', param=param)
    else:
        hash = request.form['hash']
        if hashlist.checkhash(hash):
            user = hashlist.checkhash(hash)
            shadow1 = restapi.getuser(user)
            newpassword = request.form['newpassword']
            newpassword2 = request.form['newpassword2']
            if len(newpassword) or len(newpassword2):
                if not newpassword == newpassword2:
                    param['ctrl']['errormsg'] = 'New Password and Repeat New Password doesnt match'
                    param['ctrl']['hash'] = hash
                    return render_template('reset', param=param)
                password = pbkdf2_sha256.encrypt(newpassword, rounds=200000, salt_size=16)
            else:
                param['ctrl']['errormsg'] = 'You have to type in a new password'
                param['ctrl']['hash'] = hash
                return render_template('reset', param=param)
            data = {'user': user, 'name': shadow1['data'][0]['name'], 'password': password, 'mail': shadow1['data'][0]['mail']}
            shadow1 = restapi.updateuser(data)
            param['ctrl']['okmsg'] = 'Password has been updated'
            hashlist.removehash(hash)
            return render_template('error', param=param)
        else:
            param['ctrl']['errormsg'] = 'No active password reset'
            return render_template('error', param=param)


def mail_setup():
    global mail
    mail = smtp.mailSMTP()
    config = mail.get_config()
    setconfig = {}
    for mkey, dict in config.items():
        for key, value in dict.items():
            if gcfg.get_cfg('frontend', key):
                setconfig[key] = gcfg.get_cfg('frontend', key)
            else:
                setconfig[key] = value
    mail.set_min_config(setconfig)


#def start_frontend(queue, argd):
#    global gqueue
#    global gcfg
#    global hashlist

#    gqueue = queue
#    gcfg = config.Config('.lct', 'lctfrontend')

    # Frontend listen address and port is taken from start argument
    # If it's not given check config file otherwise use default
    # The rest could be configured through web interface
#    if 'addr' in argd.keys():
#        gcfg.set_cfg('frontend', 'listen_address', argd['addr'])
#    elif not gcfg.get_cfg('frontend', 'listen_address'):
#        gcfg.set_cfg('frontend', 'listen_address', "0.0.0.0")
#    if 'port' in argd.keys():
#        gcfg.set_cfg('frontend', 'listen_port', argd['port'])
#    elif not gcfg.get_cfg('frontend', 'listen_address'):
#        gcfg.set_cfg('frontend', 'listen_port', '5050')

#    if not gcfg.get_cfg('frontend', 'backend_host'):
#        gcfg.set_cfg('frontend', 'backend_host', '0.0.0.0')
#    backend_host = gcfg.get_cfg('frontend', 'backend_host')
#    if not gcfg.get_cfg('frontend', 'backend_port'):
#        gcfg.set_cfg('frontend', 'backend_port', '5000')
#    if not gcfg.get_cfg('frontend', 'admin_password'):
#       gcfg.set_cfg('frontend', 'admin_password', 'admin')
#    backend_port = gcfg.get_cfg('frontend', 'backend_port')
#    if not gcfg.get_cfg('frontend', 'seed'):
#        gcfg.set_cfg('frontend', 'seed', str(random.randint(1,10001)))
#    seed = int(gcfg.get_cfg('frontend', 'seed'))
#    restapi.setbaseurl(backend_host, backend_port)
#    hashlist = hashlist.Hashlist(seed)

#    mail_setup()

#    app.secret_key = 'super secret key'
#    app.config['SESSION_TYPE'] = 'filesystem'
#    sess.init_app(app)

#    serve(app, listen=gcfg.get_cfg('frontend', 'listen_address') + ':' + gcfg.get_cfg('frontend', 'listen_port'),trusted_proxy="*")

def initialize():
    global gcfg
    global hashlist
    global restapi

    app = Flask(__name__)
    sess = Session()
    restapi = rest.CurlREST()

    gcfg = config.Config('.lct', 'lctfrontend')
    if not gcfg.get_cfg('frontend', 'backend_host'):
        gcfg.set_cfg('frontend', 'backend_host', '0.0.0.0')
    backend_host = gcfg.get_cfg('frontend', 'backend_host')
    if not gcfg.get_cfg('frontend', 'backend_port'):
        gcfg.set_cfg('frontend', 'backend_port', '5000')
    if not gcfg.get_cfg('frontend', 'admin_password'):
       gcfg.set_cfg('frontend', 'admin_password', 'admin')
    backend_port = gcfg.get_cfg('frontend', 'backend_port')
    if not gcfg.get_cfg('frontend', 'seed'):
        gcfg.set_cfg('frontend', 'seed', str(random.randint(1,10001)))
    seed = int(gcfg.get_cfg('frontend', 'seed'))
    restapi.setbaseurl(backend_host, backend_port)
    hashlist = hashlist.Hashlist(seed)

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)

    app.register_blueprint(tapp)
    return app

if __name__ == '__main__':
    app = initialize()
    app.run()
#    frontend_parameter = {}
#    parser = argparse.ArgumentParser(description='Lean Coffe Table frontend')
#    parser.add_argument('-l', '--listen_address', help='Frontend listen address', required=False)
#    parser.add_argument('-p', '--listen_port', help='Frontend listen port', required=False)
#    args = parser.parse_args()

#    if args.listen_address:
#        frontend_parameter['addr'] = args.listen_address
#    if args.listen_port:
#        frontend_parameter['port'] = args.listen_port

#    daemon = Daemon(start_frontend)
#    daemon.start(frontend_parameter)
