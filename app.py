import os
import json
from flask import Flask, render_template, request, redirect, url_for
from google import genai
from dotenv import load_dotenv
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

# Initialize Flask application
app = Flask(__name__)

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
    Handles JSON parsing of the API response and extracts game name.
    """
    try:
        response_text = request.args.get("response_text", "")
        
        return render_template('dashboard.html', response_text=response_text)
    
    except json.JSONDecodeError:
        # Handle invalid JSON responses
        error_message = "Automatic Memory does not recognise that game."
        return render_template('dashboard.html', error_message=error_message)

@app.route('/submit', methods=['POST'])
def submit():
    """
    Handle form submissions and interact with Gemini API.
    Generates a query for game crossplay information and processes the response.
    """
    try:
        video_game = request.form['video-game']
        
        # Construct API query with specific JSON format requirements
        query = f"""Search {video_game} on Google to find which platforms I can play this game on. Also search for details about cross play between platforms. 

        Notes:
        If for crossplay, any certain settings need to be changed, or any account linking, or only certain editions are compatible, then state so. 
        Search reddit for crossplay information.
        If a game is available on PC, list each storefront as a separate entry
        . Don't say Microsoft Windows. 
        Assume the reader is technologically versed and does not need layman's distinction.
        If a platform is no longer available, or a game is no longer available on a certain platform, then append it with (no longer available).

        Please output in json format and nothing extra:

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
        
        # Extract platforms and crossplay info
        platforms = response_data['platforms']
        crossplay = response_data['crossplay']
        
        # Pass the data to the template
        return render_template('dashboard.html', 
                            video_game=video_game,
                            platforms=platforms,
                            crossplay=crossplay)
    
    except Exception as e:
        # Handle any API or processing errors
        error_message = f"An error occurred: {str(e)}"
        return render_template('dashboard.html', error_message=error_message)

# Run the application in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)