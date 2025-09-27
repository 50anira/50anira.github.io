import os
from flask import Flask, redirect, request, session, render_template
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Required for session management


# SmugMug API credentials
CONSUMER_KEY = os.getenv("SMUGMUG_API_KEY")
CONSUMER_SECRET = os.getenv("SMUGMUG_API_SECRET")

# OAuth 1.0a endpoints
REQUEST_TOKEN_URL = "https://api.smugmug.com/services/oauth/1.0a/getRequestToken"
AUTHORIZE_URL = "https://api.smugmug.com/services/oauth/1.0a/authorize"
ACCESS_TOKEN_URL = "https://api.smugmug.com/services/oauth/1.0a/getAccessToken"
CALLBACK_URI = "https://ssd25.com/callback"

# --- Homepage Route ---
@app.route('/')
def home():
    return render_template('index.html')

# --- Connect to SmugMug Route ---
@app.route('/connect-smugmug')
def connect_smugmug():
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri=CALLBACK_URI)
    fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)

    session['resource_owner_key'] = fetch_response.get('oauth_token')
    session['resource_owner_secret'] = fetch_response.get('oauth_token_secret')

    authorization_url = oauth.authorization_url(AUTHORIZE_URL)
    return redirect(authorization_url)

# --- Callback Route ---
@app.route('/callback')
def callback():
    verifier = request.args.get('oauth_verifier')

    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=session['resource_owner_key'],
        resource_owner_secret=session['resource_owner_secret'],
        verifier=verifier
    )

    access_token_response = oauth.fetch_access_token(ACCESS_TOKEN_URL)

    access_token = access_token_response.get('oauth_token')
    access_token_secret = access_token_response.get('oauth_token_secret')

    # ✅ Place this line right here
    user_data = get_user_profile(access_token, access_token_secret)

    if user_data:
        nickname = user_data['Response']['User']['NickName']
        return f"Connected! Nickname: {nickname}<br>Access Token: {access_token}<br>Access Token Secret: {access_token_secret}"
    else:
        return "Failed to fetch user profile", 500


# --- Function to Fetch User Profile ---
def get_user_profile(access_token, access_token_secret):
    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )

    response = oauth.get("https://api.smugmug.com/api/v2!authuser")

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None


