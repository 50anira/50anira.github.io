import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load your credentials from environment variables
SMUGMUG_API_KEY = os.getenv('SMUGMUG_API_KEY')
SMUGMUG_API_SECRET = os.getenv('SMUGMUG_API_SECRET')

# The base URL for your website
REDIRECT_URI = "https://ssd25.com/callback"

# --- Homepage Route ---
@app.route('/')
def home():
    auth_url = (
        "https://secure.smugmug.com/services/oauth/2.0/authorize"
        f"?client_id={SMUGMUG_API_KEY}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return render_template('index.html', auth_url=auth_url)

# --- Callback Route ---
@app.route('/callback')
def callback():
    # Get the temporary code from the URL SmugMug sent the user to
    auth_code = request.args.get('code')
    
    # Now, exchange the code for an access token
    token_url = "https://secure.smugmug.com/services/oauth/2.0/accessToken"
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SMUGMUG_API_KEY,
        'client_secret': SMUGMUG_API_SECRET
    }
    
    response = requests.post(token_url, data=payload)
    
    if response.status_code == 200:
        # Success! We have the access token.
        access_token = response.json().get('access_token')
        # For now, we'll just display it to confirm it works.
        # In the future, we would save this token securely.
        return f"Success! Your Access Token is: {access_token}"
    else:
        # Something went wrong.
        return f"Error getting token: {response.text}", 500