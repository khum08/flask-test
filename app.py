from flask import Flask, render_template, request, jsonify

from config import DevConfig, ProConfig
from flask_login import LoginManager, login_required, login_user
import json
import os
from flask_mongoengine import MongoEngine
import random

from models import *

# application
app = Flask(__name__)
app.config.from_object(DevConfig)

# db
db = MongoEngine(app)

# login module
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"

basedir = os.path.abspath(os.path.dirname(__file__))
download_floder = os.path.join(basedir, "download")

@login_manager.user_loader
def user_loader(user_id):
    return User.objects(id=user_id).first()

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        error_msg = {
            'result': 'no'
        }
        params = json.loads(request.data.decode('utf-8'))
        username = params.get("username", "")
        password = params.get("password", "")
        if not username:
            error_msg['msg'] = 'no username'
            return jsonify(error_msg)
        if not password:
            error_msg['msg'] = 'no password'
            return jsonify(error_msg)
        user = User.objects(username=username).first()
        if not user:
            error_msg['msg'] = 'user not exist'
            return jsonify(error_msg)
        if not user.verify_password(password):
            error_msg['msg'] = 'password incorrect'
            return jsonify(error_msg)
        login_user(user)
        return jsonify({
            "result": "ok",
            "next_url": "/"
        })
        
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        error_msg = {
            'result': 'no'
        }
        param = json.loads(request.data.decode("utf-8"))
        username = param.get("username", "")
        password = param.get("password", "")
        nickname = param.get("nickname", "")
        if not nickname:
            error_msg['msg'] = 'no nickname'
            return jsonify(error_msg)
        if not username:
            error_msg['msg'] = 'no username'
            return jsonify(error_msg)
        if not password:
            error_msg['msg'] = 'no password'
            return jsonify(error_msg)
        
        user = User.objects(username=username)
        if not user:
            random_folder = random.randint(0, 10000)
            while random_folder in os.listdir(download_floder):
                random_folder = random.randint(0, 10000)
            user = User(username=username, nickname=nickname, floder=str(random_folder))
            user.hash_password(password)
            os.mkdir(os.path.join(download_floder, str(random_folder)))
            return jsonify({
                'result': 'ok'
            })
        else: 
            error_msg['msg'] = 'user exist'
            return jsonify(error_msg)
    elif request.method == 'GET':
        return render_template('register.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=20000)
