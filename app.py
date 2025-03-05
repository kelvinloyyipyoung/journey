import os
import json
from flask import Flask, render_template, request, redirect, url_for
from google import genai
from dotenv import load_dotenv

# Initialize Flask application
app = Flask(__name__)

# Configure API client
load_dotenv()
api_key = os.environ.get("API_KEY")
client = genai.Client(api_key=api_key)

@app.route('/')
def dashboard():
    """
    Main dashboard route that displays game crossplay information.
    Handles JSON parsing of the API response and extracts game name.
    """
    try:
        response_text = request.args.get("response_text", "")
        
        # Clean up JSON string from API markdown formatting
        response_text = response_text.lstrip("```json").rstrip("`").strip()
        
        # Parse response into dictionary
        response_dict = json.loads(response_text) if response_text else {}
        
        # Extract and remove game name from dictionary
        game_name = response_dict.pop("game_name", "")
        return render_template('dashboard.html', response_dict=response_dict, game_name=game_name)
    
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
        query = f"""Where can I play {video_game}? 
        Format the answer as a json string, 
        with the first key pair as ["game_name", game name],
        and the rest of the key pairs as [console, which other consoles it is able to crossplay with as a comma separated string].
        Do not add crossplay as its own key pair under any circumstance.
        If PC only has crossplay with other PC storefronts, then mention them too."""
        
        # Make API request
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=query
        )
        response_text = response.text
        return redirect(url_for('dashboard', response_text=response_text))
    
    except Exception as e:
        # Handle any API or processing errors
        error_message = f"An error occurred: {str(e)}"
        return render_template('dashboard.html', error_message=error_message)

# Run the application in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)