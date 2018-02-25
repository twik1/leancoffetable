from flask import Flask, render_template, request, redirect, url_for, session
import rest
from flask.ext.session import Session


app = Flask(__name__)
sess = Session()


@app.route('/')
def index():
    param = restapi.getboards()
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

    if param['ctrl']['response'] == 0:
        param['ctrl']['errormsg'] = 'No contact with backend'
        return render_template('error.html', param=param)

    return render_template('index.html',param=param)


@app.route('/login.html',methods=['GET', 'POST'])
def login():
    param = {}
    param['data'] = []
    param['ctrl'] = {}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

    if request.method == 'POST':
        ret = restapi.get('http://localhost:5000/lct/api/v1.0/users/'+request.form['user'])
        if ret['response'] == 0:
            param['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        if not ret['response'] == 200:
            param['errormsg'] = 'Faulty user or password'
            return render_template('login.html', param=param)
        else:
            if ret['datalist'][0]['password'] == request.form['password']:
                session['username'] = request.form['user']
                param['loggedin'] = 'yes'
                return redirect(url_for('index'))
            else:
                param['errormsg'] = 'Faulty user or password'
                return render_template('login.html', param=param)
    else:
        return render_template('login.html', param=param)


@app.route('/logout.html',methods=['GET'])
def logout():
    param = {}
    param['data'] = []
    param['ctrl'] = {}
    if 'username' in session.keys():
        session.pop('username')
    return render_template('login.html', param=param)


@app.route('/newuser.html',methods=['GET', 'POST'])
def newuser():
    param = {}
    param['data'] = []
    param['ctrl'] = {}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

    if request.method == 'POST':
        user = request.form['user']
        name = request.form['name']
        password = request.form['password']
        data = {'user': user,'name':name, 'password':password}
        ret = restapi.post('http://localhost:5000/lct/api/v1.0/users', data)
        if ret['response'] == 0:
            param['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        if ret['response'] == 201:
            session['username'] = request.form['user']
            param['ctrl']['loggedin'] = 'yes'
            param['ctrl']['sessionname'] = session['username']
            return redirect(url_for('index', param=param))
            #return render_template('index.html', param=param)
    else:
        return render_template('newuser.html', param=param)



@app.route('/newboard',methods=['GET','POST'])
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
        if startdate == '':
            startdate = '1970-01-01T00:00'
        data = {'username':username,'boardname':boardname, 'startdate':startdate}
        if restapi.post('http://localhost:5000/lct/api/v1.0/boards', data):
            return redirect(url_for('index'))
        else:
            param['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
    else:
        return render_template('newboard.html',param=param)


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
            param['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        if not ret['response'] == 200:
            param['errormsg'] = 'No such board'
            return render_template('login.html', param=param)
        if not ret['datalist'][0]['user'] == session['username']:
            param['errormsg'] = 'Can not delete anyone else board'
            return render_template('error.html', param=param)
        else:
            ret = restapi.delete('http://localhost:5000/lct/api/v1.0/boards/' + boardid)
            if ret['response'] == 0:
                param['errormsg'] = 'No contact with backend'
                return render_template('error.html', param=param)
            if not ret['response'] == 201:
                param['errormsg'] = 'No such board'
                return render_template('error.html', param=param)
            else:
                return redirect(url_for('index'))
    else:
        param['errormsg'] = 'You need to be logged in to delete a board'
        return render_template('error.html', param=param)


@app.route('/board/<boardid>')
def board(boardid):
    param = {}
    param ['ctrl'] ={}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']
    param = restapi.gettopics(boardid, param)
    param['ctrl']['boardid'] = boardid
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
        data = {'heading':topicheading,'description':topicdesc,'user':session['username']}
        if restapi.post('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics', data):
            return redirect(url_for('board',boardid=boardid))
        else:
            param['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
    else:
        return render_template('newtopic.html',param=param)


@app.route('/boards/<boardid>/deltopic/<topicid>',methods=['GET'])
def deltopic(boardid, topicid):
    param = {}
    param ['ctrl'] ={}
    if 'username' in session.keys():
        param['ctrl']['loggedin'] = 'yes'
        param['ctrl']['sessionname'] = session['username']

        ret = restapi.get('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics/'+topicid)
        if ret['response'] == 0:
            param['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
        if not ret['response'] == 200:
            param['errormsg'] = 'No such topic'
            return render_template('error.html', param=param)
        if not ret['datalist'][0]['user'] == session['username']:
            param['errormsg'] = 'Can not delete anyone else topic'
            return render_template('error.html', param=param)
        else:
            ret = restapi.delete('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics/'+topicid)
            if ret['response'] == 0:
                param['errormsg'] = 'No contact with backend'
                return render_template('error.html', param=param)
            if not ret['response'] == 201:
                param['errormsg'] = 'No such board'
                return render_template('error.html', param=param)
            else:
                return redirect(url_for('board',boardid=boardid))
    else:
        param['errormsg'] = 'You need to be logged in to delete a board'
        return render_template('error.html', param=param)


@app.route('/boards/<boardid>/topics/<topicid>/votes',methods=['GET'])
def newvote(boardid, topicid):
    if 'username' in session.keys():
        data = {'user': session['username'], 'topicid': topicid}
        ret = restapi.post('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics/'+topicid+'/votes', data)
    return redirect(url_for('board', boardid=boardid))


@app.route('/boards/<boardid>/topics/<topicid>/votes/<voteid>',methods=['GET'])
def delvote(boardid, topicid, voteid):
    if 'username' in session.keys():
       ret = restapi.delete('http://localhost:5000/lct/api/v1.0/boards/'+boardid+'/topics/'+topicid+'/votes/'+voteid)
    return redirect(url_for('board', boardid=boardid))



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)

    restapi = rest.CurlREST()
    app.run(debug=True, host='192.168.0.200', port=5050)
