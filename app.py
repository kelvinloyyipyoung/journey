import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
from google import genai
from dotenv import load_dotenv
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Configure API client
load_dotenv()
api_key = os.environ.get("API_KEY")
client = genai.Client(api_key=api_key)
model_id = "gemini-2.0-flash"

google_search_tool = Tool(
    google_search = GoogleSearch()
)

@app.route('/')
def dashboard():
    """
    Main dashboard route that displays game crossplay information.
    Gets data from session instead of URL parameters.
    """
    try:
        # Get data from session instead of request.args
        game_name = session.pop('game_name', None)
        platforms = session.pop('platforms', None)
        crossplay = session.pop('crossplay', None)
        error_message = session.pop('error_message', None)

        return render_template('dashboard.html',
                            game_name=game_name,
                            platforms=platforms,
                            crossplay=crossplay,
                            error_message=error_message)
    
    except json.JSONDecodeError:
        error_message = "Journey does not recognise that game."
        return render_template('dashboard.html', error_message=error_message)

@app.route('/', methods=['POST'])
def submit():
    """
    Handle form submissions and interact with Gemini API.
    Stores results in session instead of URL parameters.
    """
    try:
        video_game = request.form['video-game']
        
        # Construct API query with specific JSON format requirements
        query = f"""Search {video_game} on Google to find which platforms I can play this game on. Also search for details about cross play between platforms. 

        Notes:
        If for crossplay, any certain settings need to be changed, or any account linking, or only certain editions are compatible, then state so. 
        Search reddit for crossplay information.
        If a game is available on PC, list each storefront as a separate entry. Don't say Microsoft Windows. 
        Assume the reader is technologically versed and does not need layman's distinction.
        If a platform is no longer available, do not include it.
        Limit crossplay information to 100 words, and print in plain english, no markdown.

        Please output in json format and nothing extra:

        'game_name': <content here>

        'platforms': [
            'Steam',
            'macOS (no longer available)',
            'Linux',
            'Xbox 360 (no longer available)',
            'PlayStation 3 (no longer available)'
        ],
        'crossplay': <content here>"""

        
        # Make API request
        response = client.models.generate_content(
            model=model_id, contents=query, config=GenerateContentConfig(
                tools=[google_search_tool], 
                response_modalities=['TEXT']
            )
        )
        response_text = response.text
        response_text = response_text.strip("`json ")

        # Parse the response text as JSON
        response_data = json.loads(response_text)
        
        # Store in session instead of URL parameters
        session['game_name'] = response_data['game_name']
        session['platforms'] = response_data['platforms']
        session['crossplay'] = response_data['crossplay']
        
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        session['error_message'] = f"An error occurred: {str(e)}"
        return redirect(url_for('dashboard'))

# Run the application in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)