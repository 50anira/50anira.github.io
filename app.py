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
    return render_template('index.html')

# --- Secret Gallery Route ---
@app.route('/gallery/<album_key>')
def gallery(album_key):
    if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        return "Server configuration error.", 500

    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )

    try:
        # First, get the Album object itself to find its Node ID
        album_info_url = f"https://api.smugmug.com/api/v2/album/{album_key}"
        album_info_response = oauth.get(album_info_url, headers={'Accept': 'application/json'})
        album_info_response.raise_for_status()
        node_id_with_prefix = album_info_response.json()['Response']['Album']['NodeID']
        
        # --- FIX: Strip the "n-" prefix from the Node ID ---
        if node_id_with_prefix.startswith('n-'):
            actual_node_id = node_id_with_prefix.split('-')[1]
        else:
            actual_node_id = node_id_with_prefix

        # Now, use the corrected Node ID to fetch the images
        images_url = f"https://api.smugmug.com/api/v2/node/{actual_node_id}!images?_expand=ImageSizeDetails"
        images_response = oauth.get(images_url, headers={'Accept': 'application/json'})
        images_response.raise_for_status()
        
        images = images_response.json()['Response']['NodeImage']
        
        return render_template('gallery.html', images=images)

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, there was an error fetching the gallery from SmugMug.", 500