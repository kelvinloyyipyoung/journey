# Pouch

Pouch is a web application built with Flask that provides information about crossplay capabilities for various video games across different platforms. It utilizes the Google GenAI API to fetch relevant data and presents it in a user-friendly format.

## Features

- Search for any video game, old or new, to find out which platforms they are available on.
- Get detailed information about crossplay between platforms.
- User-friendly interface with a responsive design.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework for Python.
- **Google GenAI**: Used for generating content based on user queries.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/pouch.git
   cd pouch
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the root directory and add your API keys:

   ```plaintext
   API_KEY=your_google_genai_api_key
   SECRET_KEY=your_secret_key
   ```

## Running the Application

To run the application in development mode, use the following command:

```bash
python app.py
```

The application will be accessible at `http://127.0.0.1:5000/`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## Acknowledgments

- Thanks to the creators of Flask and Google GenAI for their amazing tools.