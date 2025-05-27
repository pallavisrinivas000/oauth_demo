from flask import Flask, session, render_template, redirect, url_for, request
import requests
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 16 bytes = 32 hex characters

@app.route('/')
def home():
    user = session.get('user')
    return render_template('home.html', user=user)

@app.route('/login')
def login():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}&scope=read:user"
    )
    return redirect(github_auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code
        }
    )
    access_token = token_res.json().get('access_token')
    user_res = requests.get(
        "https://api.github.com/user",
        headers={
            'Authorization': f'token {access_token}',
            'Accept': 'application/json'
        }
    )
    user = user_res.json()
    session['user'] = user
    return redirect("/")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect("/")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

    