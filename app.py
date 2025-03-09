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
def index():
    """
    Main index route that displays game crossplay information.
    Gets data from session instead of URL parameters.
    """
    error_message = session.pop('error_message', None)  # Retrieve error message first

    try:
        game_name = session.pop('game_name', None)  # Use pop with default value
        platforms = session.pop('platforms', None)  # Use pop with default value
        crossplay = session.pop('crossplay', None)  # Use pop with default value
    except KeyError:
        game_name = None
        platforms = None 
        crossplay = None

    return render_template('index.html',
                        game_name=game_name,
                        platforms=platforms,
                        crossplay=crossplay,
                        error_message=error_message)  # Pass error_message to template

@app.route('/', methods=['POST'])
def submit():
    """
    Handle form submissions and interact with Gemini API.
    Stores results in session instead of URL parameters.
    """
    try:
        video_game = request.form['video-game']
        
        # Construct API query with specific JSON format requirements
        query = f"""Your task is to find which platforms {video_game} is available on, and information about crossplay. 

        Important:
        Use grounding with google search to find platform availability.
        Use grounding with google search to search reddit for crossplay information.
        Take the general accepted meaning for the search string, I.e. lol stands for league of legends, ow stands for overwatch.
        If for crossplay, any certain settings need to be changed, or any account linking, or only certain editions are compatible, then state so. 
        If a game is available on PC, list each storefront as a separate entry. Don't say Microsoft Windows. 
        Assume the reader is technologically versed and does not need layman's distinction.
        Limit crossplay information to 100 words, and print in plain english, no markdown.
        If you cannot find the game, output "Game not found"
        Do not output your thought process:

        Once you have all the information, output it as a json object. You must use double quotes for the keys and values.

        'game_name': <content here>

        'platforms': [
            'Steam',
            'macOS (no longer available)',
            'Linux',
            'Xbox 360 (no longer available)',
            'PlayStation 3 (no longer available)'
        ],
        'crossplay': <content here>

        """

        
        # Make API request
        response = client.models.generate_content(
            model=model_id, contents=query, config=GenerateContentConfig(
                tools=[google_search_tool], 
                response_modalities=['TEXT']
            )
        )
        response_text = response.text
        response_text = response_text.strip("```json\n")
        

        # Parse the response text as JSON
        response_data = json.loads(response_text)
        
        # Store in session instead of URL parameters
        session['game_name'] = response_data['game_name']
        session['platforms'] = response_data['platforms']
        session['crossplay'] = response_data['crossplay']
        
        return redirect(url_for('index'))
    
    except Exception as e:
        session['error_message'] = f"An error occurred: {str(e)}"
        return redirect(url_for('index'))

# Run the application in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)