from flask import Flask, render_template

# Initialize the Flask app
app = Flask(__name__)

# This defines the route for your homepage
@app.route('/')
def home():
    # This tells Flask to find and show the 'index.html' file
    return render_template('index.html')