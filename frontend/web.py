from flask import Flask, render_template, request, redirect, url_for
import rest

app = Flask(__name__)


@app.route('/')
def index():
    #response = requests.get('http://localhost:5000/lct/api/v1.0/boards', headers=headers)
    restapi.getboards()
    return render_template('index.html')


@app.route('/login.html',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ret = restapi.get('http://localhost:5000/lct/api/v1.0/users/'+request.form['user'])
        if ret['response'] == 0:
            return render_template('error.html', errormsg='No contact with backend')
        if not ret['response'] == 200:
            return render_template('login.html', errormsg="Faulty user or password")
        else:
            if ret['password'] == request.form['password']:
                return render_template('index.html')
            else:
                return render_template('login.html', errormsg="Faulty user or password")
    else:
        return render_template('login.html')


@app.route('/newuser.html',methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        user = request.form['user']
        name = request.form['name']
        password = request.form['password']
        data = {'user': user,'name':name, 'password':password}
        ret = restapi.post('http://localhost:5000/lct/api/v1.0/users', data)
        if ret['response'] == 0:
            return render_template('error.html', errormsg='No contact with backend')
        if ret['response'] == 201:
            return render_template('login.html')
    else:
        return render_template('newuser.html')



@app.route('/addboard.html',methods=['GET','POST'])
def addboard():
    if request.method == 'POST':
        username = request.form['username']
        boardname = request.form['boardname']
        data = {'user':username,'name':boardname}
        if restapi.post('http://localhost:5000/lct/api/v1.0/boards', data):
            return redirect(url_for('index'))
        else:
            return render_template('error.html', errormsg='No contact with backend')
    else:
        return render_template('addboard.html')


if __name__ == '__main__':
    restapi = rest.CurlREST()
    app.run(debug=True, host='192.168.0.200', port=5050)
