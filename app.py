import os
from flask import Flask, redirect, request, session, render_template, url_for
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# SmugMug API credentials
CONSUMER_KEY = os.getenv("SMUGMUG_API_KEY")
CONSUMER_SECRET = os.getenv("SMUGMUG_API_SECRET")

# OAuth 1.0a endpoints
REQUEST_TOKEN_URL = "https://api.smugmug.com/services/oauth/1.0a/getRequestToken"
AUTHORIZE_URL = "https://api.smugmug.com/services/oauth/1.0a/authorize"
ACCESS_TOKEN_URL = "https://api.smugmug.com/services/oauth/1.0a/getAccessToken"
CALLBACK_URI = "https://ssd25.com/callback"

# --- Helper function to create an authenticated session ---
def get_smugmug_session(token=None, token_secret=None, verifier=None):
    return OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=token,
        resource_owner_secret=token_secret,
        callback_uri=CALLBACK_URI,
        verifier=verifier
    )

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/connect-smugmug')
def connect_smugmug():
    try:
        oauth = get_smugmug_session()
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
        session['request_token'] = fetch_response.get('oauth_token')
        session['request_token_secret'] = fetch_response.get('oauth_token_secret')
        authorization_url = oauth.authorization_url(AUTHORIZE_URL)
        return redirect(authorization_url)
    except Exception as e:
        print(f"Error in /connect-smugmug: {e}")
        return "Error connecting to SmugMug. Check logs.", 500

@app.route('/callback')
def callback():
    try:
        oauth = get_smugmug_session(
            token=session['request_token'],
            token_secret=session['request_token_secret'],
            verifier=request.args.get('oauth_verifier')
        )
        access_token_response = oauth.fetch_access_token(ACCESS_TOKEN_URL)

        # Store the final access tokens in the session
        session['access_token'] = access_token_response.get('oauth_token')
        session['access_token_secret'] = access_token_response.get('oauth_token_secret')

        return redirect(url_for('albums'))
    except Exception as e:
        print(f"Error in /callback: {e}")
        return "Error authenticating with SmugMug. Check logs.", 500

@app.route('/albums')
def albums():
    if 'access_token' not in session:
        return redirect(url_for('home'))

    try:
        oauth = get_smugmug_session(
            token=session['access_token'],
            token_secret=session['access_token_secret']
        )
        
        profile_response = oauth.get("https://api.smugmug.com/api/v2!authuser", headers={'Accept': 'application/json'})
        if profile_response.status_code != 200:
            return "Could not fetch user profile.", 500
        
        nickname = profile_response.json()['Response']['User']['NickName']
        
        albums_url = f"https://api.smugmug.com/api/v2/user/{nickname}!albums?count=100"
        
        albums_response = oauth.get(albums_url, headers={'Accept': 'application/json'})
        if albums_response.status_code != 200:
            return "Could not fetch albums.", 500
            
        all_albums = albums_response.json()['Response']['Album']
        
        # --- CORRECTED FILTER ---
        # We now look for albums where SecurityType is 'None' (Unlisted)
        public_albums = [album for album in all_albums if album.get('SecurityType') == 'None']
        
        album_titles = [album['Title'] for album in public_albums]
        
        # Remove the debugging print statements
        return "<h2>Your Albums:</h2>" + "<br>".join(album_titles)

    except Exception as e:
        print(f"Error in /albums: {e}")
        return "An error occurred while fetching albums. Check logs.", 500