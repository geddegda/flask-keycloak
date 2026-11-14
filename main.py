import os
from flask import Flask, redirect, url_for, session, render_template_string
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
#app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.secret_key = "superb" # whatever

oauth = OAuth(app)
oauth.register(
    name="keycloak",
    client_id="webapp",
    client_secret="whatever", # whatever
    server_metadata_url="http://keycloak.local.couincouin.click:8080/realms/guillaume_local_realm/.well-known/openid-configuration",
    authorize_url='http://keycloak.local.couincouin.click:8080/realms/guillaume_local_realm/protocol/openid-connect/auth',
    client_kwargs={"scope": "openid profile email"},
)

@app.route("/")
def index():
    user = session.get("user")
    if user:        
        return render_template_string('''
		<h1> This is the APPLICATION SSO ENABLED #1 </h1>
            <h2>Welcome, {{ user['name'] }}!</h2>
            <form action="{{ url_for('logout') }}" method="post">
                <button type="submit">Logout</button>
            </form>
        ''', user=user)
    else:        
        return render_template_string('''
		<h1> This is the APPLICATION SSO ENABLED #1 </h1>
            <h2>Hello, you are not logged in.</h2>
            <form action="{{ url_for('login') }}" method="post">
                <button type="submit">Login</button>
            </form>
        ''')

# Login page
@app.route("/login", methods=["POST"])
def login():
    redirect_uri = url_for("auth", _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri)

# Auth callback
@app.route("/auth")
def auth():
    token = oauth.keycloak.authorize_access_token()
    session["user"] = oauth.keycloak.parse_id_token(token, None)
    return redirect("/")

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    logout_url = f"http://keycloak.local.couincouin.click:8080/realms/guillaume_local_realm/protocol/openid-connect/logout?client_id=webapp&post_logout_redirect_uri={url_for('index', _external=True)}"
    return redirect(logout_url)

if __name__ == "__main__":
    app.run(host="192.168.1.206", port=80)
