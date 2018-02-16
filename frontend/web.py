from flask import Flask, render_template, request, redirect, url_for, session
import rest
from flask.ext.session import Session


app = Flask(__name__)
sess = Session()


@app.route('/')
def index():
    param = {}
    if 'username' in session.keys():
        param['loggedin'] = 'yes'
        param['username'] = session['username']
    boardlist = restapi.getboards()
    param['boardlist'] = boardlist
    return render_template('index.html',param=param)


@app.route('/login.html',methods=['GET', 'POST'])
def login():
    param = {}
    if 'username' in session.keys():
        param['loggedin'] = 'yes'
        param['username'] = session['username']

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
    if 'username' in session.keys():
        session.pop('username')
    return render_template('login.html', param=param)


@app.route('/newuser.html',methods=['GET', 'POST'])
def newuser():
    param = {}
    if 'username' in session.keys():
        param['loggedin'] = 'yes'
        param['username'] = session['username']

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
            param['loggedin'] = 'yes'
            return render_template('index.html', param=param)
    else:
        return render_template('newuser.html', param=param)



@app.route('/addboard.html',methods=['GET','POST'])
def addboard():
    param = {}
    if 'username' in session.keys():
        param['loggedin'] = 'yes'
        param['username'] = session['username']

    if request.method == 'POST':
        username = request.form['username']
        boardname = request.form['boardname']
        startdate = request.form['startdate']
        data = {'username':username,'boardname':boardname, 'startdate':startdate}
        if restapi.post('http://localhost:5000/lct/api/v1.0/boards', data):
            return redirect(url_for('index'))
        else:
            param['errormsg'] = 'No contact with backend'
            return render_template('error.html', param=param)
    else:
        return render_template('addboard.html',param=param)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)

    restapi = rest.CurlREST()
    app.run(debug=True, host='192.168.0.200', port=5050)
