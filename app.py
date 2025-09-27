import os
from flask import Flask, render_template
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load all four of your permanent credentials from Render's Environment Variables
CONSUMER_KEY = os.getenv("SMUGMUG_API_KEY")
CONSUMER_SECRET = os.getenv("SMUGMUG_API_SECRET")
ACCESS_TOKEN = os.getenv("SMUGMUG_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("SMUGMUG_ACCESS_TOKEN_SECRET")

@app.route('/')
def home():
    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )

    try:
        profile_response = oauth.get("https://api.smugmug.com/api/v2!authuser", headers={'Accept': 'application/json'})
        profile_response.raise_for_status()
        nickname = profile_response.json()['Response']['User']['NickName']
        
        # Add the _expand parameter to the URL to request the cover image
        albums_url = f"https://api.smugmug.com/api/v2/user/{nickname}!albums?count=100&_expand=AlbumCoverImage"
        
        albums_response = oauth.get(albums_url, headers={'Accept': 'application/json'})
        albums_response.raise_for_status()
        
        all_albums = albums_response.json()['Response']['Album']
        public_albums = [album for album in all_albums if album.get('SecurityType') != 'Password']
        
        return render_template('index.html', albums=public_albums)

    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return "Sorry, there was an error fetching data from SmugMug. Check the logs for details.", 500