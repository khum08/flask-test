from flask import Flask, redirect, render_template, request, jsonify, send_from_directory

from config import DevConfig, ProConfig
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
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

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        return render_template('index.html', 
                               folder=current_user.folder,
                               nickname=current_user.nickname
                               )
    elif request.method == 'POST':
        return 'post'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login');

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
            user = User(username=username, nickname=nickname, folder=str(random_folder))
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


@app.route('/get_list', methods=['GET'])
def get_list():
    response_json = {
        'result': 'No'
    }
    folder = os.path.join(download_floder, current_user.folder)
    if not os.path.exists(folder):
        response_json['msg'] = 'folder does not exist'
        return jsonify(response_json)
    file_list = os.listdir(folder)
    response_json['result'] = file_list
    return jsonify(response_json)


@app.route('/upload', methods=['POST'])
def upload():
    response_json = {
        'result': 'No'
    }
    file = request.files['file']
    folder = os.path.join(download_floder, current_user.folder)
    if not os.path.exists(folder):
        os.mkdir(folder)
    file.save(os.path.join(folder, file.filename))
    print(os.path.join(folder, file.filename))
    response_json['result'] = 'ok'
    return jsonify(response_json)

@app.route('/download/<string:filename>')
@login_required
def download(filename):
    response_json = {
        'result': 'No'
    }
    if not os.path.exists(os.path.join(download_floder, current_user.folder, filename)):
        response_json['msg'] = 'no such file'
        return jsonify(response_json)
    return send_from_directory(os.path.join(download_floder, current_user.folder), filename, as_attachment=True)

@app.route('/delete/<string:filename>')
@login_required
def delete_file(filename):
    response_json = {
        'result': 'No'
    }
    if not os.path.exists(os.path.join(download_floder, current_user.folder, filename)):
        response_json['msg'] = 'no such file'
        return jsonify(response_json)
    os.remove(os.path.join(download_floder, current_user.folder, filename))
    response_json['result'] = 'ok'
    return jsonify(response_json)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=20000)
