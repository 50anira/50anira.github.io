import os
from flask import Flask, render_template
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load all four of your permanent credentials
CONSUMER_KEY = os.getenv("SMUGMUG_API_KEY")
CONSUMER_SECRET = os.getenv("SMUGMUG_API_SECRET")
ACCESS_TOKEN = os.getenv("SMUGMUG_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("SMUGMUG_ACCESS_TOKEN_SECRET")

# --- Homepage Route (Your Key Finder) ---
@app.route('/')
def home():
    if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        return "Server configuration error: Missing one or more API credentials in Environment Variables.", 500
    
    oauth = OAuth1Session(
        CONSUMER_KEY, client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN, resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    try:
        profile_response = oauth.get("https://api.smugmug.com/api/v2!authuser", headers={'Accept': 'application/json'})
        profile_response.raise_for_status()
        nickname = profile_response.json()['Response']['User']['NickName']
        
        albums_url = f"https://api.smugmug.com/api/v2/user/{nickname}!albums?count=100"
        albums_response = oauth.get(albums_url, headers={'Accept': 'application/json'})
        albums_response.raise_for_status()
        
        all_items = albums_response.json()['Response']['Album']
        
        key_list_html = "<h1>Your SmugMug Keys</h1><ul>"
        for item in all_items:
            key_list_html += f"<li><b>{item['Title']}</b><br/>Album Key: {item.get('AlbumKey', 'N/A')}<br/>Node ID: {item.get('NodeID', 'N/A')}</li><br/>"
        key_list_html += "</ul>"
        return key_list_html
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error fetching album keys."

# --- Final Album Gallery Route ---
@app.route('/album/<album_key>')
def album(album_key):
    if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        return "Server configuration error.", 500
        
    oauth = OAuth1Session(
        CONSUMER_KEY, client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN, resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    try:
        images_url = f"https://api.smugmug.com/api/v2/album/{album_key}!images?_expand=ImageSizeDetails"
        images_response = oauth.get(images_url, headers={'Accept': 'application/json'})
        images_response.raise_for_status()
        
        images = images_response.json()['Response']['AlbumImage']
        return render_template('gallery.html', images=images)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, there was an error fetching the album from SmugMug.", 500