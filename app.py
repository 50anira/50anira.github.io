import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# This defines the route for your homepage
@app.route('/')
def home():
    # You can now access your keys like this (we will use them later)
    api_key = os.getenv('SMUGMUG_API_KEY')
    api_secret = os.getenv('SMUGMUG_API_SECRET')
    
    # For now, just print them to the Render log to confirm they are working
    print(f"API Key found: {api_key}")
    
    return render_template('index.html')