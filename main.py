from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import os
from tinydb import TinyDB, Query


app = Flask(__name__)
app.secret_key = "fffff"

@app.route("/login")
def init():
    return render_template('login.html')

@app.route("/login", methods=['POST'])
def login():
    token = request.form['token']
    session.pop('token',None)
    session['token'] = token
    return redirect(url_for('load'))


@app.route("/", methods=['GET','POST'])
def load():
    global db
    db = TinyDB('db.json')
    users = db.table('users')
    admin = db.table('admin')
    if not 'token' in session:
        return redirect(url_for('login'))
    token = session['token']
    token_search = users.search(Query().token==token)
    if not token_search:
        return redirect(url_for('login'))
    global df
    filestring = str(users.search(Query().token==token)[0]['filestring'])
    df = pd.read_csv(filestring) #change this to take dynamic filename from the database
    global length
    length = len(df)
    progress = int(users.search(Query().token==token)[0]['progress'])
    task = users.search(Query().token==token)[0]['task']
    user = users.search(Query().token==token)[0]['user']
    taskid = users.search(Query().token==token)[0]['taskid']
    question = admin.search(Query().taskid==taskid)[0]['question']
    options = admin.search(Query().taskid==taskid)[0]['options']
    if request.method == 'POST':
            option = request.form['option']
            df.loc[progress,user] = option
            df.to_csv(filestring,index=False)
            df = pd.read_csv(filestring)
            progress = progress + 1
    if progress == length:
        # df = df.drop('options', axis=1)
        # df.to_csv(filestring,index=False)
        users.update({'progress':-1}, Query().token==token)
        return render_template('end.html', user=user)
    elif progress==-1:
        return render_template('end.html', user=user)
    else:
        users.update({'progress':progress}, Query().token==token)
        print "sad"
        return render_template('index.html', data=df.heading[progress], user=user, task=task, question=question, options=options.split("|"))

@app.route("/logout")
def logout():
    print "sex"
    session.pop('token',None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT',8080))
    app.run(host='0.0.0.0', port=port, threaded = True)
