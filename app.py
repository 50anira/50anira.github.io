import os
from flask import Flask, render_template
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load all four of your permanent credentials with the correct names
CONSUMER_KEY = os.getenv("SMUGMUG_API_KEY")
CONSUMER_SECRET = os.getenv("SMUGMUG_API_SECRET")
ACCESS_TOKEN = os.getenv("SMUGMUG_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("SMUGMUG_ACCESS_TOKEN_SECRET")

# --- Homepage Route ---
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
        
        albums_url = f"https://api.smugmug.com/api/v2/user/{nickname}!albums?count=100"
        albums_response = oauth.get(albums_url, headers={'Accept': 'application/json'})
        albums_response.raise_for_status()
        
        all_albums = albums_response.json()['Response']['Album']
        public_albums = [album for album in all_albums if album.get('SecurityType') != 'Password']
        
        # Create a simple HTML list of album titles and their keys
        key_list_html = "<h1>Album and Page Keys</h1><ul>"
        for item in public_albums:
            # Differentiate between Albums and Pages (Nodes)
            if 'AlbumKey' in item:
                key_list_html += f"<li><b>{item['Title']} (Album):</b> {item['AlbumKey']}</li>"
            if 'NodeID' in item:
                 key_list_html += f"<li><b>{item['Title']} (Page/Node):</b> {item['NodeID']}</li>"
        key_list_html += "</ul>"
        
        return key_list_html

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error fetching album keys."
# @app.route('/')
# def home():
#     return render_template('index.html')

# --- Secret Gallery Route ---
@app.route('/gallery/<album_key>')
def gallery(album_key):
    # This check will stop the app if any key is missing and print a clear error
    if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("One or more SmugMug environment variables are not set.")
        return "Server configuration error. Check logs.", 500

    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )

    try:
        # --- FIX: Strip the "n-" prefix from the album_key ---
        if album_key.startswith('n-'):
            actual_key = album_key.split('-')[1]
        else:
            actual_key = album_key

        images_url = f"https://api.smugmug.com/api/v2/album/{actual_key}!images?_expand=ImageSizeDetails"
        
        images_response = oauth.get(images_url, headers={'Accept': 'application/json'})
        images_response.raise_for_status()
        
        images = images_response.json()['Response']['AlbumImage']
        
        return render_template('gallery.html', images=images)

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, there was an error fetching the album from SmugMug.", 500