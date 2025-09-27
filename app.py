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
    # Create a pre-authenticated session using your permanent tokens
    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )

    try:
        # Get your user nickname
        profile_response = oauth.get("https://api.smugmug.com/api/v2!authuser", headers={'Accept': 'application/json'})
        profile_response.raise_for_status()
        nickname = profile_response.json()['Response']['User']['NickName']
        
        # Fetch up to 100 of your albums
        albums_url = f"https://api.smugmug.com/api/v2/user/{nickname}!albums?count=100"
        albums_response = oauth.get(albums_url, headers={'Accept': 'application/json'})
        albums_response.raise_for_status()
        
        all_albums = albums_response.json()['Response']['Album']
        
        # Filter for albums that are NOT private
        public_albums = [album for album in all_albums if album.get('SecurityType') != 'Password']
        
        # Pass the list of public albums to the HTML template
        return render_template('index.html', albums=public_albums)

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, there was an error fetching data from SmugMug.", 500