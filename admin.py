from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import os
from tinydb import TinyDB, Query
import random
import string


app = Flask(__name__)
app.secret_key = "fffff"

@app.route("/admin", methods=['GET','POST'])
def admin():
    if request.method == "GET":
        return render_template("admin.html")
    elif request.method == "POST":
        task = request.form['task']
        question = request.form['question']
        options = request.form['options']
        annotators = request.form['annotators']
        global db
        db = TinyDB('db.json')
        admin = db.table('admin')
        taskid = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        f = request.files['file']
        filestring = (str(taskid) + str(f.filename))
        f.save(filestring)
        admin.insert({'taskid':taskid,'task':task,'question':question,'options':options,'filestring':filestring})
        users = db.table('users')
        annotators = annotators.split('|')
        user_array = []
        for annotator in annotators:
            token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            user_array.append([annotator,token])
            users.insert({'user':annotator,'token':token,'progress':0,'task':task,'taskid':taskid,'filestring':filestring})
        return render_template('users.html',users=user_array)

if __name__ == '__main__':
    port = int(os.environ.get('PORT',8080))
    app.run(host='0.0.0.0', port=port, threaded = True)
