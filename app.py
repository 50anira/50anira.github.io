import os
from flask import Flask, render_template
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load all four of your permanent credentials
CONSUMER_KEY = os.getenv("SMUGMug_API_KEY")
CONSUMER_SECRET = os.getenv("SMUGMug_API_SECRET")
ACCESS_TOKEN = os.getenv("SMUGMug_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("SMUGMug_ACCESS_TOKEN_SECRET")

# --- Homepage Route ---
@app.route('/')
def home():
    # This page will now just show a simple template
    return render_template('index.html')

# --- Secret Gallery Route ---
@app.route('/gallery/<album_key>')
def gallery(album_key):
    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )

    try:
        # Construct the URL to get a specific album's images
        # We also expand the ImageSizeDetails to get a good thumbnail URL
        images_url = f"https://api.smugmug.com/api/v2/album/{album_key}!images?_expand=ImageSizeDetails"
        
        images_response = oauth.get(images_url, headers={'Accept': 'application/json'})
        images_response.raise_for_status()
        
        # Get the list of images from the response
        images = images_response.json()['Response']['AlbumImage']
        
        # Pass the list of images to a new gallery template
        return render_template('gallery.html', images=images)

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, there was an error fetching the album from SmugMug.", 500