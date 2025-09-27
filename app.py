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

# --- Homepage Route (Simple Landing Page) ---
@app.route('/')
def home():
    return render_template('index.html')

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